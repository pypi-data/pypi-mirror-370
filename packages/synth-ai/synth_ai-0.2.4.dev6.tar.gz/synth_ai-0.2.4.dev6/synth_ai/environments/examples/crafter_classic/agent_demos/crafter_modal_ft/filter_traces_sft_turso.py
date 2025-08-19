#!/usr/bin/env python3
"""
Filter traces from Turso/SQLite (v3) to create Modal/Synth SFT-ready .jsonl files
Supports two modes:
1. Trajectory-level filtering: Include entire trajectories above a score threshold
2. Window-based filtering: Extract high-scoring windows of actions

This is the v3 version using the new async Turso-based tracing system.
"""

import json
import argparse
import asyncio
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
from collections import defaultdict
import numpy as np
import os
import sys
import toml
import pandas as pd

# Add synth_ai to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

from synth_ai.tracing_v3 import SessionTracer
from synth_ai.tracing_v3.turso.manager import AsyncSQLTraceManager
from synth_ai.tracing_v3.abstractions import LMCAISEvent, EnvironmentEvent, RuntimeEvent


def create_histogram(data: List[float], bins: int = 20, width: int = 60, height: int = 15, 
                    title: str = "", x_label: str = "", y_label: str = "") -> str:
    """Create a beautiful ASCII histogram."""
    if not data:
        return "No data to display"
    
    # Create histogram
    counts, edges = np.histogram(data, bins=bins)
    max_count = max(counts) if len(counts) > 0 else 1
    
    # Normalize heights
    if max_count > 0:
        heights = [int(c * height / max_count) for c in counts]
    else:
        heights = [0] * len(counts)
    
    # Build the plot
    lines = []
    
    # Title
    if title:
        lines.append(f"\n{title.center(width + 10)}")
        lines.append("=" * (width + 10))
    
    # Y-axis label
    if y_label:
        lines.append(f"{y_label}")
    
    # Plot area with y-axis
    for y in range(height, 0, -1):
        # Y-axis value
        y_val = int(max_count * y / height)
        line = f"{y_val:>6} │"
        
        # Bars
        for h in heights:
            if h >= y:
                line += "█"
            else:
                line += " "
        
        lines.append(line)
    
    # X-axis
    lines.append(f"{'':>6} └" + "─" * len(heights))
    
    # X-axis labels
    x_labels_line = " " * 8
    min_val, max_val = min(data), max(data)
    
    # Add labels at key positions
    label_positions = [0, len(heights)//4, len(heights)//2, 3*len(heights)//4, len(heights)-1]
    for i, pos in enumerate(label_positions):
        if pos < len(edges) - 1:
            val = edges[pos]
            label = f"{val:.1f}"
            # Calculate position
            target_pos = 8 + pos
            if i == 0:
                x_labels_line = label + x_labels_line[len(label):]
            elif i == len(label_positions) - 1:
                start = max(0, target_pos - len(label))
                x_labels_line = x_labels_line[:start] + label
            else:
                start = max(0, target_pos - len(label)//2)
                end = min(len(x_labels_line), start + len(label))
                if start < len(x_labels_line):
                    x_labels_line = x_labels_line[:start] + label[:end-start] + x_labels_line[end:]
    
    lines.append(x_labels_line)
    
    # X-axis label
    if x_label:
        lines.append(f"\n{x_label.center(width + 10)}")
    
    return "\n".join(lines)


def create_bar_chart(categories: List[str], values: List[int], width: int = 60, 
                     title: str = "", show_values: bool = True) -> str:
    """Create a horizontal bar chart."""
    if not categories or not values:
        return "No data to display"
    
    max_val = max(values) if values else 1
    lines = []
    
    # Title
    if title:
        lines.append(f"\n{title}")
        lines.append("=" * (width + 20))
    
    # Find longest category name for alignment
    max_cat_len = max(len(cat) for cat in categories)
    
    # Create bars
    for cat, val in zip(categories, values):
        # Normalize bar length
        bar_len = int(val * width / max_val) if max_val > 0 else 0
        bar = "█" * bar_len
        
        # Format line
        if show_values:
            line = f"{cat:<{max_cat_len}} │ {bar} {val}"
        else:
            line = f"{cat:<{max_cat_len}} │ {bar}"
        
        lines.append(line)
    
    return "\n".join(lines)


class FinetuningDataExtractorV3:
    """Extract fine-tuning data from v3 Turso traces."""
    
    def __init__(self, db_url: str):
        self.db_manager = AsyncSQLTraceManager(db_url)
        self._initialized = False
    
    async def __aenter__(self):
        await self.db_manager.initialize()
        self._initialized = True
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.db_manager.close()
    
    async def get_all_sessions(self) -> pd.DataFrame:
        """Get all session IDs from the database."""
        query = """
        SELECT DISTINCT session_id, created_at
        FROM session_traces
        ORDER BY created_at DESC
        """
        return await self.db_manager.query_traces(query)
    
    async def get_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get metrics for a specific session."""
        # Get total reward from environment events
        # Now that rewards are properly saved in the DB, we can use them directly
        reward_query = """
        SELECT COALESCE(SUM(reward), 0) as total_reward
        FROM events
        WHERE session_id = :session_id
        AND event_type = 'environment'
        AND reward IS NOT NULL
        """
        reward_df = await self.db_manager.query_traces(reward_query, {"session_id": session_id})
        total_reward = float(reward_df['total_reward'].iloc[0]) if not reward_df.empty else 0.0
        
        # Get total tokens and cost from LM events
        lm_query = """
        SELECT 
            COALESCE(SUM(total_tokens), 0) as total_tokens,
            COALESCE(SUM(cost_usd) / 100.0, 0) as total_cost
        FROM events
        WHERE session_id = :session_id
        AND event_type = 'cais'
        """
        lm_df = await self.db_manager.query_traces(lm_query, {"session_id": session_id})
        
        total_tokens = int(lm_df['total_tokens'].iloc[0]) if not lm_df.empty else 0
        total_cost = float(lm_df['total_cost'].iloc[0]) if not lm_df.empty else 0.0
        
        return {
            'session_id': session_id,
            'total_reward': total_reward,
            'total_tokens': total_tokens,
            'total_cost': total_cost
        }
    
    async def get_session_achievements(self, session_id: str) -> List[str]:
        """Get list of achievements unlocked in a session."""
        # Look for achievement events in environment data
        # In v3, system_state_after is a direct column
        query = """
        SELECT system_state_after
        FROM events
        WHERE session_id = :session_id
        AND event_type = 'environment'
        AND system_state_after IS NOT NULL
        ORDER BY id DESC
        LIMIT 1
        """
        df = await self.db_manager.query_traces(query, {"session_id": session_id})
        
        if df.empty:
            return []
        
        try:
            # Parse the system_state_after JSON
            state_after = df['system_state_after'].iloc[0]
            if state_after:
                # If it's a string, parse it
                if isinstance(state_after, str):
                    state_after = json.loads(state_after)
                
                # Look for achievements in public_state
                if isinstance(state_after, dict) and 'public_state' in state_after:
                    public_state = state_after['public_state']
                    if 'achievements_status' in public_state:
                        achievements = public_state['achievements_status']
                        # Return list of unlocked achievements
                        return [k for k, v in achievements.items() if v]
        except Exception as e:
            print(f"Error parsing achievements: {e}")
            pass
        
        return []
    
    async def filter_by_achievements(self, min_achievements: int) -> List[str]:
        """Get sessions with at least min_achievements unlocked."""
        all_sessions = await self.get_all_sessions()
        qualifying_sessions = []
        
        for _, row in all_sessions.iterrows():
            session_id = row['session_id']
            achievements = await self.get_session_achievements(session_id)
            if len(achievements) >= min_achievements:
                qualifying_sessions.append(session_id)
        
        return qualifying_sessions
    
    async def extract_openai_format_from_call_records(self, session_ids: List[str], min_reward: float = 0.0) -> List[Dict[str, Any]]:
        """Extract training data in OpenAI format from call_records in LMCAISEvents.
        
        This is the new method that uses the detailed LLM interaction data stored
        in call_records instead of relying on separate message records.
        """
        training_data = []
        
        for session_id in session_ids:
            # Get LM CAIS events with call_records from the proper column
            events_query = """
            SELECT e.call_records, st.turn_number
            FROM events e
            LEFT JOIN session_timesteps st ON e.timestep_id = st.id
            WHERE e.session_id = :session_id
            AND e.event_type = 'cais'
            AND e.call_records IS NOT NULL
            ORDER BY COALESCE(st.turn_number, e.message_time), e.id
            """
            
            events_df = await self.db_manager.query_traces(events_query, {"session_id": session_id})
            
            if len(events_df) == 0:
                # Fall back to old method if no call_records
                continue
            
            # Extract messages from call_records
            all_messages = []
            
            for _, row in events_df.iterrows():
                call_records_json = row['call_records']
                if not call_records_json:
                    continue
                
                # Parse the call_records JSON directly from the column
                try:
                    import json
                    if isinstance(call_records_json, str):
                        call_records = json.loads(call_records_json)
                    else:
                        call_records = call_records_json
                    
                    # Process each call record
                    for record in call_records:
                        # Extract input messages
                        for msg in record.get('input_messages', []):
                            role = msg.get('role', 'user')
                            parts = msg.get('parts', [])
                            
                            # Combine text parts
                            text_content = []
                            for part in parts:
                                if part.get('type') == 'text' and part.get('text'):
                                    text_content.append(part['text'])
                            
                            if text_content:
                                content = ' '.join(text_content)
                                if role == 'system' and not any(m['role'] == 'system' for m in all_messages):
                                    all_messages.insert(0, {"role": "system", "content": content})
                                elif role != 'system':
                                    all_messages.append({"role": role, "content": content})
                        
                        # Extract output messages
                        for msg in record.get('output_messages', []):
                            role = msg.get('role', 'assistant')
                            parts = msg.get('parts', [])
                            
                            # Combine text parts
                            text_content = []
                            for part in parts:
                                if part.get('type') == 'text' and part.get('text'):
                                    text_content.append(part['text'])
                            
                            if text_content:
                                content = ' '.join(text_content)
                                all_messages.append({"role": role, "content": content})
                
                except Exception as e:
                    print(f"Error parsing call_records for session {session_id}: {e}")
                    continue
            
            # Only include if we have a complete conversation
            if len(all_messages) > 1:
                # Get total reward for this session
                reward_query = """
                SELECT COALESCE(SUM(reward), 0) as total_reward
                FROM events
                WHERE session_id = :session_id
                AND event_type = 'environment'
                AND reward IS NOT NULL
                """
                reward_df = await self.db_manager.query_traces(reward_query, {"session_id": session_id})
                total_reward = reward_df.iloc[0]['total_reward'] if len(reward_df) > 0 else 0
                
                training_data.append({
                    "messages": all_messages,
                    "metadata": {
                        "session_id": session_id,
                        "total_reward": float(total_reward),
                        "source": "call_records"  # Mark that this came from call_records
                    }
                })
        
        return training_data
    
    async def extract_openai_format(self, session_ids: List[str], min_reward: float = 0.0) -> List[Dict[str, Any]]:
        """Extract training data in OpenAI format from filtered sessions."""
        training_data = []
        
        for session_id in session_ids:
            # Get messages directly from the messages table
            messages_query = """
            SELECT m.message_type, m.content, m.message_time, st.turn_number
            FROM messages m
            LEFT JOIN session_timesteps st ON m.timestep_id = st.id
            WHERE m.session_id = :session_id
            ORDER BY COALESCE(st.turn_number, m.message_time), m.id
            """
            
            messages_df = await self.db_manager.query_traces(messages_query, {"session_id": session_id})
            
            if len(messages_df) == 0:
                continue
            
            # Build conversation history
            messages = []
            system_message = None
            
            for _, row in messages_df.iterrows():
                msg_type = row['message_type']
                content = row['content']
                
                # Parse content if it's JSON (from origin_system_id format)
                try:
                    import json
                    content_data = json.loads(content)
                    if isinstance(content_data, dict) and 'payload' in content_data:
                        content = content_data['payload']
                except:
                    pass
                
                if msg_type == 'system' and system_message is None:
                    # Extract system message from the first system message
                    if isinstance(content, str):
                        system_message = content
                
                elif msg_type == 'user':
                    # Format user messages
                    if isinstance(content, dict):
                        # Convert observation dict to formatted string
                        content = self._format_observation_content(content)
                    messages.append({"role": "user", "content": str(content)})
                    
                elif msg_type == 'assistant':
                    messages.append({"role": "assistant", "content": str(content)})
            
            # Add system message at the beginning if found
            if system_message:
                messages.insert(0, {"role": "system", "content": system_message})
            
            # Only include if we have a complete conversation
            if len(messages) > 1:
                # Get total reward for this session
                reward_query = """
                SELECT COALESCE(SUM(reward), 0) as total_reward
                FROM events
                WHERE session_id = :session_id
                AND event_type = 'environment'
                AND reward IS NOT NULL
                """
                reward_df = await self.db_manager.query_traces(reward_query, {"session_id": session_id})
                total_reward = reward_df.iloc[0]['total_reward'] if len(reward_df) > 0 else 0
                
                training_data.append({
                    "messages": messages,
                    "metadata": {
                        "session_id": session_id,
                        "total_reward": float(total_reward)  # Convert to float for JSON serialization
                    }
                })
        
        return training_data
    
    def _format_observation_content(self, obs: Dict[str, Any]) -> str:
        """Format observation dict into a readable string."""
        if not isinstance(obs, dict):
            return str(obs)
        
        # Extract key fields for a concise representation
        parts = []
        
        if 'inventory' in obs:
            inv = obs['inventory']
            inv_str = ", ".join([f"{k}: {v}" for k, v in inv.items() if v > 0])
            if inv_str:
                parts.append(f"Inventory: {inv_str}")
        
        if 'achievements_status' in obs:
            achievements = [k for k, v in obs['achievements_status'].items() if v]
            if achievements:
                parts.append(f"Achievements: {', '.join(achievements)}")
        
        if 'health' in obs:
            parts.append(f"Health: {obs.get('health', 0)}")
        
        return "; ".join(parts) if parts else "Empty observation"


async def filter_traces_from_turso(
    db_url: str,
    output_path: str,
    config: Dict[str, Any]
) -> Tuple[int, Dict[str, Any]]:
    """
    Filter traces from Turso/SQLite v3 database based on configuration.
    
    Returns:
        Tuple of (num_examples, statistics_dict)
    """
    mode = config.get("mode", "trajectory")
    filters = config.get("filters", {})
    
    # Extract filtering parameters
    min_reward = filters.get("min_total_reward", 0.0)
    min_achievements = filters.get("min_achievements", 0)
    max_cost = filters.get("max_cost", float('inf'))
    max_tokens = filters.get("max_tokens", float('inf'))
    
    # Modal/Synth specific: filter by model if specified
    target_models = filters.get("models", [])
    
    statistics = {
        "total_sessions": 0,
        "filtered_sessions": 0,
        "total_examples": 0,
        "reward_distribution": [],
        "token_distribution": [],
        "cost_distribution": [],
        "model_distribution": defaultdict(int)
    }
    
    async with FinetuningDataExtractorV3(db_url) as extractor:
        # Get all sessions
        all_sessions = await extractor.get_all_sessions()
        statistics["total_sessions"] = len(all_sessions)
        
        # Filter sessions based on criteria
        filtered_sessions = []
        
        for _, row in all_sessions.iterrows():
            session_id = row['session_id']
            metrics = await extractor.get_session_metrics(session_id)
            
            # Apply filters
            if metrics['total_reward'] < min_reward:
                continue
            if metrics['total_cost'] > max_cost:
                continue
            if metrics['total_tokens'] > max_tokens:
                continue
            
            # Check achievements if required
            if min_achievements > 0:
                achievements = await extractor.get_session_achievements(session_id)
                if len(achievements) < min_achievements:
                    continue
            
            # Check model filter if specified
            if target_models:
                model_query = """
                    SELECT DISTINCT model_name
                    FROM events
                    WHERE session_id = :session_id
                    AND event_type = 'cais'
                    AND model_name IS NOT NULL
                """
                model_df = await extractor.db_manager.query_traces(
                    model_query, {"session_id": session_id}
                )
                session_models = model_df['model_name'].tolist() if not model_df.empty else []
                if not any(model in target_models for model in session_models):
                    continue
            
            filtered_sessions.append(session_id)
            
            # Collect statistics
            statistics["reward_distribution"].append(metrics['total_reward'])
            statistics["token_distribution"].append(metrics['total_tokens'])
            statistics["cost_distribution"].append(metrics['total_cost'])
        
        statistics["filtered_sessions"] = len(filtered_sessions)
        
        # Extract training data
        if mode == "trajectory":
            # Try new method first (using call_records)
            training_data = await extractor.extract_openai_format_from_call_records(
                session_ids=filtered_sessions,
                min_reward=min_reward
            )
            
            # If no data from call_records, fall back to old method
            if not training_data:
                print("No call_records found, falling back to message-based extraction...")
                training_data = await extractor.extract_openai_format(
                    session_ids=filtered_sessions,
                    min_reward=min_reward
                )
        else:  # window mode
            # For window mode, we need to implement window extraction
            # For now, use trajectory mode
            training_data = await extractor.extract_openai_format(
                session_ids=filtered_sessions,
                min_reward=min_reward
            )
        
        statistics["total_examples"] = len(training_data)
        
        # Write to output file
        output_file = Path(output_path)
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, 'w') as f:
            for example in training_data:
                f.write(json.dumps(example) + '\n')
        
        # Get model distribution
        model_query = """
            SELECT model_name, COUNT(*) as count
            FROM events
            WHERE event_type = 'cais'
            AND model_name IS NOT NULL
            GROUP BY model_name
        """
        model_stats = await extractor.db_manager.query_traces(model_query)
        for _, row in model_stats.iterrows():
            statistics["model_distribution"][row['model_name']] = int(row['count'])
    
    return len(training_data), statistics


def print_statistics(stats: Dict[str, Any]):
    """Print filtering statistics with visualizations."""
    print("\n" + "="*80)
    print("FILTERING STATISTICS (Modal/Synth - v3)")
    print("="*80)
    
    # Basic counts
    print(f"\nTotal sessions in database: {stats['total_sessions']}")
    print(f"Sessions after filtering: {stats['filtered_sessions']}")
    print(f"Training examples generated: {stats['total_examples']}")
    
    filter_rate = (stats['filtered_sessions'] / stats['total_sessions'] * 100) if stats['total_sessions'] > 0 else 0
    print(f"Filter pass rate: {filter_rate:.1f}%")
    
    # Reward distribution
    if stats['reward_distribution'] and any(not np.isnan(x) for x in stats['reward_distribution']):
        valid_rewards = [x for x in stats['reward_distribution'] if not np.isnan(x)]
        if valid_rewards:
            print(create_histogram(
                valid_rewards,
                bins=20,
                title="Reward Distribution",
                x_label="Total Reward",
                y_label="Count"
            ))
            
            print(f"\nReward statistics:")
            print(f"  Min: {min(valid_rewards):.2f}")
            print(f"  Max: {max(valid_rewards):.2f}")
            print(f"  Mean: {np.mean(valid_rewards):.2f}")
            print(f"  Median: {np.median(valid_rewards):.2f}")
    else:
        print("\nNo valid reward data to display.")
    
    # Token distribution
    if stats['token_distribution'] and any(not np.isnan(x) for x in stats['token_distribution']):
        valid_tokens = [x for x in stats['token_distribution'] if not np.isnan(x)]
        if valid_tokens:
            print(create_histogram(
                valid_tokens,
                bins=20,
                title="Token Usage Distribution",
                x_label="Total Tokens",
                y_label="Count"
            ))
    
    # Model distribution
    if stats['model_distribution']:
        models = list(stats['model_distribution'].keys())
        counts = list(stats['model_distribution'].values())
        print(create_bar_chart(
            models,
            counts,
            title="Model Usage",
            show_values=True
        ))
    
    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(
        description="Filter traces from Turso/SQLite v3 for Modal/Synth fine-tuning",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example usage:
  # Use default config
  python filter_traces_sft_turso.py -d sqlite:///traces.db -o ft_data/training.jsonl
  
  # Use custom config file
  python filter_traces_sft_turso.py -d sqlite:///traces.db -c filter_config.toml
  
  # Override config parameters
  python filter_traces_sft_turso.py -d sqlite:///traces.db --min-reward 5.0 --max-cost 0.1
  
  # Filter by model
  python filter_traces_sft_turso.py -d sqlite:///traces.db --models "Qwen/Qwen2.5-7B-Instruct"
        """
    )
    
    parser.add_argument('-d', '--database', required=True, help='Path to Turso/SQLite database or connection URL')
    parser.add_argument('-o', '--output', default='ft_data/training_modal.jsonl', help='Output JSONL file')
    parser.add_argument('-c', '--config', help='Configuration TOML file')
    
    # Filter overrides
    parser.add_argument('--mode', choices=['trajectory', 'window'], help='Filtering mode')
    parser.add_argument('--min-reward', type=float, help='Minimum total reward')
    parser.add_argument('--min-achievements', type=int, help='Minimum achievements')
    parser.add_argument('--max-cost', type=float, help='Maximum cost')
    parser.add_argument('--max-tokens', type=int, help='Maximum tokens')
    parser.add_argument('--models', nargs='+', help='Filter by model names (e.g., Qwen/Qwen2.5-7B-Instruct)')
    
    parser.add_argument('--dry-run', action='store_true', help='Show statistics without writing output')
    
    args = parser.parse_args()
    
    # Load config
    config = {
        "mode": "trajectory",
        "filters": {
            "min_total_reward": 1.0,
            "min_achievements": 0,
            "max_cost": 10.0,
            "max_tokens": 100000,
            "models": []  # Empty means all models
        }
    }
    
    if args.config:
        with open(args.config, 'r') as f:
            loaded_config = toml.load(f)
            config.update(loaded_config)
    
    # Apply command-line overrides
    if args.mode:
        config["mode"] = args.mode
    if args.min_reward is not None:
        config["filters"]["min_total_reward"] = args.min_reward
    if args.min_achievements is not None:
        config["filters"]["min_achievements"] = args.min_achievements
    if args.max_cost is not None:
        config["filters"]["max_cost"] = args.max_cost
    if args.max_tokens is not None:
        config["filters"]["max_tokens"] = args.max_tokens
    if args.models:
        config["filters"]["models"] = args.models
    
    # Convert database path to proper URL format if needed
    db_url = args.database
    if db_url.startswith("sqlite:///"):
        # Already in URL format
        pass
    elif db_url.endswith(".db"):
        # Convert file path to URL
        db_url = f"sqlite+aiosqlite:///{db_url}"
    
    print(f"🤖 Modal/Synth Fine-Tuning Data Filter (v3)")
    print(f"Using database: {db_url}")
    print(f"Output file: {args.output}")
    print(f"Mode: {config['mode']}")
    print(f"Filters: {json.dumps(config['filters'], indent=2)}")
    
    if args.dry_run:
        print("\n🔍 DRY RUN - No output will be written")
    
    # Run filtering
    async def run():
        num_examples, stats = await filter_traces_from_turso(
            db_url,
            args.output if not args.dry_run else "/dev/null",
            config
        )
        
        # Print statistics
        print_statistics(stats)
        
        if not args.dry_run:
            print(f"\n✅ Successfully wrote {num_examples} training examples to {args.output}")
            print(f"   Ready for Modal/Synth fine-tuning!")
        else:
            print(f"\n✅ Would write {num_examples} training examples (dry run)")
    
    asyncio.run(run())


if __name__ == "__main__":
    main()