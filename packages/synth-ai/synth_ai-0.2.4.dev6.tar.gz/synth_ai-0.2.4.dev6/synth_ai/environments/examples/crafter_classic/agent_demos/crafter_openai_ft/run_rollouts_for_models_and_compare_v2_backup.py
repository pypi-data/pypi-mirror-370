#!/usr/bin/env python3
"""
Comprehensive script to run Crafter rollouts for multiple models and compare their performance.

Runs experiments for:
- gpt-4o-mini
- gpt-4.1-mini  
- gpt-4.1-nano
- gemini-1.5-flash
- gemini-2.5-flash-lite
- qwen3/32b

Analyzes and compares:
- Invalid action rates
- Achievement frequencies by step
- Achievement counts across models
- Performance metrics
- Cost analysis
"""

import asyncio
import json
import uuid
import argparse
import logging
import time
import toml
from datetime import datetime
from typing import Dict, Any, Optional, List, Set, Tuple
from pathlib import Path
import sys
import os
from collections import defaultdict, Counter
import pandas as pd
import numpy as np
from tqdm.asyncio import tqdm_asyncio
from tqdm import tqdm
import duckdb

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent.parent))

# Disable v1 logging to see v2 tracing clearly
os.environ["LANGFUSE_ENABLED"] = "false"
os.environ["SYNTH_LOGGING"] = "false"

# Import enhanced LM with v2 tracing
from synth_ai.lm.core.main_v2 import LM

# Import session tracer for v2 tracing
from synth_ai.tracing_v2.session_tracer import (
    SessionTracer, SessionEventMessage, TimeRecord,
    RuntimeEvent, EnvironmentEvent, LMCAISEvent
)
from synth_ai.tracing_v2.utils import create_experiment_context
from synth_ai.tracing_v2.duckdb.manager import DuckDBTraceManager
from synth_ai.tracing_v2.decorators import (
    set_active_session_tracer, set_system_id, set_turn_number
)

# Import Crafter hooks
try:
    from synth_ai.environments.examples.crafter_classic.trace_hooks import CRAFTER_HOOKS
    print(f"✅ Loaded {len(CRAFTER_HOOKS)} Crafter achievement hooks (Easy, Medium, Hard)")
except ImportError:
    print("Warning: Could not import CRAFTER_HOOKS")
    CRAFTER_HOOKS = []

import httpx
import random

# Global buckets for sessions
_SESSIONS: dict[str, tuple[str, object]] = {}  # session_id -> (experiment_id, trace)

# Configuration
MODELS_TO_TEST = [
    "gpt-4o-mini",
    #"gpt-4.1-mini", 
    "gpt-4.1-nano",
    # "gemini-1.5-flash",
    # "gemini-2.5-flash-lite",
]

# Service URLs (modify these based on your setup)
CRAFTER_SERVICE_URL = "http://localhost:8901"
DATABASE_PATH = "/Users/joshuapurtell/Documents/GitHub/synth-ai/synth_ai/traces/crafter_multi_model_traces.duckdb"

# Retry configuration for HTTP requests
MAX_RETRIES = 3
BASE_DELAY = 0.1
MAX_DELAY = 2.0
HTTP_TIMEOUT = 30.0

class ExperimentConfig:
    """Configuration for the multi-model experiment."""
    
    def __init__(self):
        self.num_episodes = 10  # Number of episodes per model
        self.max_turns = 100    # Max turns per episode
        self.difficulty = "easy"
        self.save_traces = True
        self.verbose = True
        self.quiet = False      # Default to verbose mode
        self.enable_v2_tracing = True
        self.v2_trace_dir = "./traces"
        self.crafter_service_url = CRAFTER_SERVICE_URL
        self.database_path = DATABASE_PATH


async def retry_http_request(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> Any:
    """Retry HTTP requests with exponential backoff and jitter."""
    last_exception = None
    
    for attempt in range(MAX_RETRIES):
        try:
            if attempt > 0:
                delay = min(BASE_DELAY * (2 ** (attempt - 1)), MAX_DELAY)
                jitter = random.uniform(0, 0.1 * delay)
                total_delay = delay + jitter
                await asyncio.sleep(total_delay)
            
            response = await client.request(method, url, timeout=HTTP_TIMEOUT, **kwargs)
            
            if response.status_code < 500:
                return response
            
            last_exception = Exception(f"HTTP {response.status_code}: {response.text}")
            
        except httpx.ConnectError as e:
            last_exception = Exception(f"Connection failed to {url}: {e}")
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1.0 * (2 ** attempt))
        except httpx.ReadError as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                read_error_delay = min(1.0 * (2 ** attempt), 5.0)
                await asyncio.sleep(read_error_delay)
        except Exception as e:
            last_exception = e
    
    print(f"    ❌ HTTP request failed after {MAX_RETRIES} attempts: {method} {url}")
    print(f"    ❌ Error: {type(last_exception).__name__}: {str(last_exception)[:200]}")
    raise last_exception


# Crafter action mapping
CRAFTER_ACTIONS = {
    "noop": 0, "move_left": 1, "move_right": 2, "move_up": 3, "move_down": 4,
    "do": 5, "sleep": 6, "place_stone": 7, "place_table": 8, "place_furnace": 9,
    "place_plant": 10, "make_wood_pickaxe": 11, "make_stone_pickaxe": 12,
    "make_iron_pickaxe": 13, "make_wood_sword": 14, "make_stone_sword": 15,
    "make_iron_sword": 16,
    # Aliases
    "move": 5,  # "move" -> "do" (context-dependent action)
    "collect": 5,  # "collect" -> "do"
    "attack": 5,   # "attack" -> "do"
    "eat": 5,      # "eat" -> "do"
}

def action_to_int(action: str) -> int:
    """Convert action string to integer."""
    normalized = action.strip().lower().replace(" ", "_")
    return CRAFTER_ACTIONS.get(normalized, 5)  # Default to "do"


def create_message(content: Any, message_type: str, origin_system_id: Any = None, turn: int = None) -> SessionEventMessage:
    """Create a session event message."""
    return SessionEventMessage(
        content=str(content),
        message_type=message_type,
        time_record=TimeRecord(
            message_time=turn if turn is not None else 0,
            event_time=time.time()
        )
    )


def compress_observation_for_trace(obs: Dict[str, Any]) -> Dict[str, Any]:
    """Compress observation for tracing."""
    return {
        "inventory": obs.get("inventory", {}),
        "nearby": obs.get("nearby", []),
        "status": obs.get("status", {}),
        "achievement": obs.get("achievement", None)
    }


async def run_episode(episode_id: int, model_name: str, config: ExperimentConfig, 
                     session_tracer: SessionTracer) -> Dict[str, Any]:
    """Run a single episode with the specified model."""
    episode_start_time = time.time()
    episode_reward = 0.0
    step_results = []
    termination_reason = "max_steps"
    
    # Set up LM for this model
    lm = LM(
        model_name=model_name,
        formatting_model_name="gpt-4o-mini",  # Use a reliable model for formatting
        temperature=0.1,  # Low temperature for more consistent gameplay
        session_tracer=session_tracer,
        system_id=f"crafter_agent_{model_name}",
        enable_v2_tracing=True
    )
    
    # Create HTTP client
    async with httpx.AsyncClient() as client:
        try:
            # Initialize environment
            init_response = await retry_http_request(
                client, "POST", f"{config.crafter_service_url}/env/CrafterClassic/initialize",
                json={"difficulty": config.difficulty, "seed": random.randint(0, 1000000)}
            )
            init_data = init_response.json()
            
            # Debug the response format
            if config.verbose and not config.quiet:
                print(f"Init response: {init_data}")
            
            # Handle different possible response formats
            if "env_id" in init_data:
                instance_id = init_data["env_id"]
            elif "instance_id" in init_data:
                instance_id = init_data["instance_id"]
            elif "id" in init_data:
                instance_id = init_data["id"]
            else:
                # If none of the expected keys exist, print the response and raise a clear error
                print(f"❌ Unexpected response format from Crafter service: {init_data}")
                raise KeyError(f"Could not find environment ID in response. Available keys: {list(init_data.keys())}")
            
            # Get initial observation (from initialize response)
            obs = init_data["observation"]
            
            prev_obs = obs
            done = False
            invalid_actions = 0
            total_actions = 0
            
            for turn in range(config.max_turns):
                if done:
                    break
                
                set_turn_number(turn)
                
                # Start timestep for this turn
                session_tracer.start_timestep(f"turn_{turn}")
                
                # Prepare context for the agent
                inventory_str = ", ".join([f"{k}: {v}" for k, v in obs.get("inventory", {}).items() if v > 0])
                if not inventory_str:
                    inventory_str = "empty"
                
                nearby_str = ", ".join(obs.get("nearby", []))
                if not nearby_str:
                    nearby_str = "nothing"
                
                status = obs.get("status", {})
                health = status.get("health", 0)
                hunger = status.get("food", 0)
                
                # Create agent prompt
                prompt = f"""You are playing Crafter, a 2D survival game. Choose your next action.

Current status:
- Health: {health}/9
- Hunger: {hunger}/9
- Inventory: {inventory_str}
- Nearby objects: {nearby_str}

Available actions: do, move_left, move_right, move_up, move_down, place_stone, place_table, place_furnace, place_plant, make_wood_pickaxe, make_stone_pickaxe, make_iron_pickaxe, make_wood_sword, make_stone_sword, make_iron_sword, sleep

Respond with just the action name (e.g., "do" or "move_left" or "make_wood_pickaxe")."""

                # Send observation as message
                obs_msg = create_message(
                    compress_observation_for_trace(obs),
                    "observation",
                    f"crafter_env_{instance_id}",
                    turn
                )
                session_tracer.record_message(obs_msg)
                
                # Get action from LM
                try:
                    action_response = await lm.respond_async(
                        system_message="You are playing Crafter, a 2D survival game. Choose your next action.",
                        user_message=prompt,
                        turn_number=turn
                    )
                    action = action_response.raw_response.strip().lower()
                    
                    # Clean up action
                    action = action.replace('"', '').replace("'", "").strip()
                    
                    # Send action as message
                    action_msg = create_message(
                        action,
                        "action",
                        f"crafter_agent_{model_name}",
                        turn
                    )
                    session_tracer.record_message(action_msg)
                    
                except Exception as e:
                    if config.verbose and not config.quiet:
                        print(f"    ❌ LM call failed: {e}")
                    action = "do"  # Default action
                
                total_actions += 1
                
                # Convert action to integer and format correctly
                action_int = action_to_int(action)
                
                # Take action in environment
                step_response = await retry_http_request(
                    client, "POST", f"{config.crafter_service_url}/env/CrafterClassic/step",
                    json={"env_id": instance_id, "action": {"tool_calls": [{"tool": "interact", "args": {"action": action_int}}]}}
                )
                step_data = step_response.json()
                
                obs = step_data.get("observation", {})
                reward = step_data.get("reward")
                # Ensure reward is always a valid number
                if reward is None or not isinstance(reward, (int, float)):
                    if config.verbose and not config.quiet:
                        print(f"    ⚠️  Invalid reward {reward}, using 0.0")
                    reward = 0.0
                else:
                    reward = float(reward)
                    
                done = step_data.get("done", False)
                info = step_data.get("info", {})
                
                # Check if action was invalid
                if info.get("invalid_action", False):
                    invalid_actions += 1
                
                episode_reward += reward
                
                # Record step results
                step_result = {
                    "step": turn,
                    "action": action,
                    "reward": reward,
                    "invalid": info.get("invalid_action", False),
                    "achievement": obs.get("achievement"),
                    "health": obs.get("status", {}).get("health", 0),
                    "hunger": obs.get("status", {}).get("food", 0)
                }
                step_results.append(step_result)
                
                # Record runtime event
                runtime_event = RuntimeEvent(
                    system_instance_id=f"crafter_runtime_{model_name}",
                    time_record=TimeRecord(
                        event_time=datetime.now().isoformat(),
                        message_time=turn
                    ),
                    actions=[action_int],
                    metadata={
                        "step": turn,
                        "reward": reward,
                        "done": done,
                        "invalid_action": info.get("invalid_action", False),
                        "action_name": action,
                        "action_int": action_int
                    }
                )
                session_tracer.record_event(runtime_event)
                
                if done:
                    termination_reason = "environment_done"
                    break
            
            # Terminate instance
            await retry_http_request(
                client, "POST", f"{config.crafter_service_url}/env/CrafterClassic/terminate",
                json={"env_id": instance_id}
            )
            
        except Exception as e:
            print(f"❌ Episode {episode_id} failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "episode_id": episode_id,
                "model": model_name,
                "error": str(e),
                "duration": time.time() - episode_start_time
            }
    
    # Calculate metrics
    invalid_action_rate = invalid_actions / total_actions if total_actions > 0 else 0.0
    
    return {
        "episode_id": episode_id,
        "model": model_name,
        "total_reward": episode_reward,
        "steps": len(step_results),
        "termination_reason": termination_reason,
        "duration": time.time() - episode_start_time,
        "invalid_action_rate": invalid_action_rate,
        "invalid_actions": invalid_actions,
        "total_actions": total_actions,
        "step_results": step_results
    }


async def run_episode_async(episode_id: int, model_name: str, config: ExperimentConfig, 
                          experiment_id: str) -> Dict[str, Any]:
    """Run a single episode asynchronously with its own tracer."""
    # Create unique session ID with timestamp for better uniqueness
    import time
    timestamp = int(time.time() * 1000000)  # microseconds for uniqueness
    uuid_val = uuid.uuid4()
    session_id = f"episode_{episode_id}_{model_name.replace('/', '_')}_{timestamp}_{uuid_val}"
    
    # Debug session ID generation
    print(f"🔧 Generated session_id: {session_id}")
    print(f"   Episode: {episode_id}, Model: {model_name}")
    print(f"   Timestamp: {timestamp}, UUID: {uuid_val}")
    print(f"   Model name sanitized: {model_name.replace('/', '_')}")
    
    # Create individual tracer for this episode (no DB to avoid conflicts)
    tracer = SessionTracer(hooks=CRAFTER_HOOKS, duckdb_path="")
    
    # Add small delay to reduce database contention and ensure unique timestamps
    await asyncio.sleep(0.01 * episode_id)  # Staggered start times
    
    # Additional delay to ensure timestamp uniqueness
    await asyncio.sleep(0.001)  # 1ms additional delay
    
    tracer.start_session(session_id)
    
    try:
        # Run the episode
        result = await run_episode(episode_id, model_name, config, tracer)
        
        # Get reference to session before ending it
        session_to_upload = tracer.current_session
        
        # End session without uploading to DB (we'll do it at the end to avoid races)
        trace_path = tracer.end_session(save=True, upload_to_db=False)
        
        # Store session for batch upload at the end
        if session_id in _SESSIONS:
            print(f"⚠️  WARNING: Session {session_id} already in _SESSIONS! Skipping duplicate.")
            print(f"   Existing experiment_id: {_SESSIONS[session_id][0]}")
            print(f"   New experiment_id: {experiment_id}")
            print(f"   Existing trace type: {type(_SESSIONS[session_id][1])}")
            print(f"   New trace type: {type(session_to_upload)}")
            print(f"   This should NEVER happen with UUID-based session IDs!")
        else:
            _SESSIONS[session_id] = (experiment_id, session_to_upload)
            print(f"🔵 Stored session {session_id} for batch upload")
            print(f"   Experiment ID: {experiment_id}")
            print(f"   Trace type: {type(session_to_upload)}")
            if hasattr(session_to_upload, 'num_timesteps'):
                print(f"   Timesteps: {session_to_upload.num_timesteps}")
            
            # Verify uniqueness by checking all existing session IDs
            all_session_ids = list(_SESSIONS.keys())
            if len(all_session_ids) != len(set(all_session_ids)):
                print(f"🚨 CRITICAL: Session ID collision detected!")
                print(f"   Total sessions: {len(all_session_ids)}")
                print(f"   Unique sessions: {len(set(all_session_ids))}")
                print(f"   Collisions: {len(all_session_ids) - len(set(all_session_ids))}")
                from collections import Counter
                duplicates = [sid for sid, count in Counter(all_session_ids).items() if count > 1]
                print(f"   Duplicate IDs: {duplicates}")
        return result
        
    except Exception as e:
        print(f"❌ Episode {episode_id} for {model_name} failed: {e}")
        return {
            "episode_id": episode_id,
            "model": model_name,
            "error": str(e),
            "duration": 0.0
        }


async def run_experiment_for_model(model_name: str, config: ExperimentConfig) -> Tuple[str, List[Dict[str, Any]]]:
    """Run complete experiment for a single model with concurrent episodes."""
    if not config.quiet:
        print(f"\n🚀 Starting experiment for {model_name}")
        print(f"   Episodes: {config.num_episodes}")
        print(f"   Max turns: {config.max_turns}")
    
    # Create experiment ID
    experiment_id = str(uuid.uuid4())
    experiment_name = f"crafter_{model_name.replace('/', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Create experiment in database
    with DuckDBTraceManager(config.database_path) as db_manager:
        try:
            db_manager.create_experiment(
                experiment_id=experiment_id,
                name=experiment_name,
                description=f"Crafter evaluation with {model_name}"
            )
        except Exception as e:
            print(f"Warning: Could not create experiment in DB: {e}")
    
    # Create async tasks for all episodes
    episode_tasks = []
    for i in range(config.num_episodes):
        task = run_episode_async(i, model_name, config, experiment_id)
        episode_tasks.append(task)
    
    if not config.quiet:
        print(f"📍 Running {config.num_episodes} episodes concurrently for {model_name}")
    
    # Run all episodes concurrently with progress tracking
    with tqdm(total=config.num_episodes, desc=f"{model_name} Episodes") as pbar:
        results = []
        
        # Use asyncio.as_completed to get results as they finish
        for coro in asyncio.as_completed(episode_tasks):
            result = await coro
            results.append(result)
            pbar.update(1)
    
    # Sort results by episode_id to maintain order
    results.sort(key=lambda x: x.get("episode_id", 0))
    
    if not config.quiet:
        print(f"✅ Completed experiment for {model_name}")
    return experiment_id, results


def analyze_invalid_actions(all_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Analyze invalid action rates across models."""
    analysis = {}
    
    for model_name, results in all_results.items():
        successful_episodes = [r for r in results if "error" not in r]
        
        if successful_episodes:
            invalid_rates = [r["invalid_action_rate"] for r in successful_episodes]
            total_invalid = sum(r["invalid_actions"] for r in successful_episodes)
            total_actions = sum(r["total_actions"] for r in successful_episodes)
            
            analysis[model_name] = {
                "avg_invalid_rate": np.mean(invalid_rates),
                "std_invalid_rate": np.std(invalid_rates),
                "total_invalid_actions": total_invalid,
                "total_actions": total_actions,
                "overall_invalid_rate": total_invalid / total_actions if total_actions > 0 else 0.0
            }
        else:
            analysis[model_name] = {
                "avg_invalid_rate": 0.0,
                "std_invalid_rate": 0.0,
                "total_invalid_actions": 0,
                "total_actions": 0,
                "overall_invalid_rate": 0.0
            }
    
    return analysis


def analyze_achievements_by_step(all_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Analyze achievement frequencies by step across models."""
    analysis = {}
    
    for model_name, results in all_results.items():
        successful_episodes = [r for r in results if "error" not in r]
        
        achievement_by_step = defaultdict(list)
        all_achievements = []
        
        for result in successful_episodes:
            for step_result in result.get("step_results", []):
                step = step_result["step"]
                achievement = step_result.get("achievement")
                
                if achievement:
                    achievement_by_step[step].append(achievement)
                    all_achievements.append(achievement)
        
        # Count unique achievements
        achievement_counts = Counter(all_achievements)
        
        # Calculate achievement frequency by step ranges
        step_ranges = [(0, 25), (26, 50), (51, 75), (76, 100)]
        achievements_by_range = {}
        
        for range_start, range_end in step_ranges:
            range_achievements = []
            for step in range(range_start, range_end + 1):
                range_achievements.extend(achievement_by_step.get(step, []))
            
            achievements_by_range[f"{range_start}-{range_end}"] = {
                "count": len(range_achievements),
                "unique": len(set(range_achievements)),
                "achievements": list(set(range_achievements))
            }
        
        analysis[model_name] = {
            "total_achievements": len(all_achievements),
            "unique_achievements": len(set(all_achievements)),
            "achievement_counts": dict(achievement_counts),
            "achievements_by_step_range": achievements_by_range
        }
    
    return analysis


def analyze_performance_metrics(all_results: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Any]:
    """Analyze overall performance metrics across models."""
    analysis = {}
    
    for model_name, results in all_results.items():
        successful_episodes = [r for r in results if "error" not in r]
        failed_episodes = [r for r in results if "error" in r]
        
        if successful_episodes:
            rewards = [r["total_reward"] for r in successful_episodes]
            steps = [r["steps"] for r in successful_episodes]
            durations = [r["duration"] for r in successful_episodes]
            
            analysis[model_name] = {
                "total_episodes": len(results),
                "successful_episodes": len(successful_episodes),
                "failed_episodes": len(failed_episodes),
                "success_rate": len(successful_episodes) / len(results),
                "avg_reward": np.mean(rewards),
                "std_reward": np.std(rewards),
                "max_reward": np.max(rewards),
                "min_reward": np.min(rewards),
                "avg_steps": np.mean(steps),
                "avg_duration": np.mean(durations)
            }
        else:
            analysis[model_name] = {
                "total_episodes": len(results),
                "successful_episodes": 0,
                "failed_episodes": len(failed_episodes),
                "success_rate": 0.0,
                "avg_reward": 0.0,
                "std_reward": 0.0,
                "max_reward": 0.0,
                "min_reward": 0.0,
                "avg_steps": 0.0,
                "avg_duration": 0.0
            }
    
    return analysis


def print_results_summary(all_results: Dict[str, List[Dict[str, Any]]], 
                         experiment_ids: Dict[str, str]):
    """Print comprehensive results summary."""
    print("\n" + "="*100)
    print("🏆 MULTI-MODEL CRAFTER EVALUATION RESULTS")
    print("="*100)
    
    # Performance metrics
    performance_analysis = analyze_performance_metrics(all_results)
    
    print("\n📊 PERFORMANCE SUMMARY")
    print("-" * 80)
    print(f"{'Model':<20} {'Episodes':<10} {'Success%':<10} {'Avg Reward':<12} {'Avg Steps':<12} {'Avg Duration':<12}")
    print("-" * 80)
    
    for model_name in MODELS_TO_TEST:
        if model_name in performance_analysis:
            perf = performance_analysis[model_name]
            print(f"{model_name:<20} {perf['total_episodes']:<10} {perf['success_rate']*100:<9.1f}% {perf['avg_reward']:<11.2f} {perf['avg_steps']:<11.1f} {perf['avg_duration']:<11.1f}s")
    
    # Invalid action analysis
    invalid_analysis = analyze_invalid_actions(all_results)
    
    print("\n🚫 INVALID ACTION ANALYSIS")
    print("-" * 80)
    print(f"{'Model':<20} {'Avg Invalid%':<15} {'Total Invalid':<15} {'Total Actions':<15}")
    print("-" * 80)
    
    for model_name in MODELS_TO_TEST:
        if model_name in invalid_analysis:
            inv = invalid_analysis[model_name]
            print(f"{model_name:<20} {inv['avg_invalid_rate']*100:<14.2f}% {inv['total_invalid_actions']:<14} {inv['total_actions']:<14}")
    
    # Achievement analysis
    achievement_analysis = analyze_achievements_by_step(all_results)
    
    print("\n🏅 ACHIEVEMENT ANALYSIS")
    print("-" * 80)
    print(f"{'Model':<20} {'Total Ach.':<12} {'Unique Ach.':<12} {'Early (0-25)':<12} {'Mid (26-50)':<12} {'Late (51+)':<12}")
    print("-" * 80)
    
    for model_name in MODELS_TO_TEST:
        if model_name in achievement_analysis:
            ach = achievement_analysis[model_name]
            early = ach['achievements_by_step_range'].get('0-25', {}).get('count', 0)
            mid = ach['achievements_by_step_range'].get('26-50', {}).get('count', 0)
            late1 = ach['achievements_by_step_range'].get('51-75', {}).get('count', 0)
            late2 = ach['achievements_by_step_range'].get('76-100', {}).get('count', 0)
            late = late1 + late2
            
            print(f"{model_name:<20} {ach['total_achievements']:<11} {ach['unique_achievements']:<11} {early:<11} {mid:<11} {late:<11}")
    
    # Model ranking
    print("\n🥇 MODEL RANKINGS")
    print("-" * 50)
    
    # Rank by average reward
    reward_ranking = sorted([(model, perf['avg_reward']) for model, perf in performance_analysis.items()], 
                           key=lambda x: x[1], reverse=True)
    
    print("By Average Reward:")
    for i, (model, reward) in enumerate(reward_ranking, 1):
        print(f"  {i}. {model}: {reward:.2f}")
    
    # Rank by invalid action rate (lower is better)
    invalid_ranking = sorted([(model, inv['avg_invalid_rate']) for model, inv in invalid_analysis.items()], 
                            key=lambda x: x[1])
    
    print("\nBy Invalid Action Rate (lower is better):")
    for i, (model, rate) in enumerate(invalid_ranking, 1):
        print(f"  {i}. {model}: {rate*100:.2f}%")
    
    # Experiment IDs
    print("\n🆔 EXPERIMENT IDS")
    print("-" * 50)
    for model_name, exp_id in experiment_ids.items():
        print(f"{model_name}: {exp_id}")
    
    print("\n" + "="*100)


def print_comprehensive_model_analytics(database_path: str, experiment_ids: Dict[str, str], quiet: bool = False):
    """Generate comprehensive model analytics from DuckDB data."""
    try:
        from synth_ai.tracing_v2.duckdb.manager import DuckDBTraceManager
        import pandas as pd
        
        with DuckDBTraceManager(database_path) as db:
            if not quiet:
                print("\n🔍 COMPREHENSIVE MODEL ANALYTICS")
                print("=" * 80)
            
            # 1. Model Performance Summary
            print_model_performance_summary(db, experiment_ids, quiet)
            
            # 2. Achievement Analysis
            print_achievement_analysis(db, experiment_ids, quiet)
            
            # 3. Action Analysis
            print_action_analysis(db, experiment_ids, quiet)
            
            # 4. Efficiency Metrics
            print_efficiency_metrics(db, experiment_ids, quiet)
            
            # 5. Error Analysis
            print_error_analysis(db, experiment_ids, quiet)
            
    except Exception as e:
        if not quiet:
            print(f"⚠️  Failed to generate analytics: {e}")


def print_model_performance_summary(db, experiment_ids: Dict[str, str], quiet: bool):
    """Print overall model performance summary."""
    if not quiet:
        print("\n## 📊 Model Performance Summary")
        print("-" * 40)
    
    try:
        # Get session-level metrics by model (using reward from runtime metadata)
        valid_experiment_ids = [eid for eid in experiment_ids.values() if eid != "failed"]
        if not valid_experiment_ids:
            print("No performance data available")
            return
            
        query = """
        WITH session_rewards AS (
            SELECT 
                st.session_id,
                st.experiment_id,
                st.num_timesteps,
                SUM(COALESCE(CAST(json_extract(ev.metadata, '$.reward') AS DOUBLE), 0)) as session_total_reward
            FROM session_traces st
            LEFT JOIN events ev ON st.session_id = ev.session_id 
                AND ev.event_type = 'runtime' 
                AND json_extract(ev.metadata, '$.reward') IS NOT NULL
            GROUP BY st.session_id, st.experiment_id, st.num_timesteps
        )
        SELECT 
            experiment_id,
            COUNT(session_id) as episodes,
            AVG(num_timesteps) as avg_steps,
            MAX(num_timesteps) as max_steps,
            MIN(num_timesteps) as min_steps,
            AVG(session_total_reward) as avg_reward,
            SUM(session_total_reward) as total_reward
        FROM session_rewards
        WHERE experiment_id IN ({})
        GROUP BY experiment_id
        ORDER BY total_reward DESC
        """.format(','.join([f"'{eid}'" for eid in valid_experiment_ids]))
        
        df = db.query_traces(query)
        
        if df.empty:
            print("No performance data available")
            return
            
        # Map experiment IDs back to model names
        exp_to_model = {v: k for k, v in experiment_ids.items() if v != "failed"}
        df['model'] = df['experiment_id'].map(exp_to_model)
        
        # Create performance table
        if not quiet:
            print("\n| Model | Episodes | Avg Steps | Max Steps | Total Reward | Avg Reward |")
            print("|-------|----------|-----------|-----------|--------------|------------|")
            
            for _, row in df.iterrows():
                print(f"| {row['model']:<12} | {int(row['episodes']):>8} | {row['avg_steps']:>9.1f} | {int(row['max_steps']):>9} | {row['total_reward']:>12.1f} | {row['avg_reward']:>10.3f} |")
        else:
            # Quiet mode - just show winners
            if not df.empty and 'total_reward' in df.columns and 'avg_reward' in df.columns:
                valid_total_df = df[df['total_reward'].notna()]
                valid_avg_df = df[df['avg_reward'].notna()]
                
                if not valid_total_df.empty:
                    best_reward = valid_total_df.loc[valid_total_df['total_reward'].idxmax()]
                    print(f"🏆 Best Total Reward: {best_reward['model']} ({best_reward['total_reward']:.1f})")
                
                if not valid_avg_df.empty:
                    best_efficiency = valid_avg_df.loc[valid_avg_df['avg_reward'].idxmax()]
                    print(f"⚡ Most Efficient: {best_efficiency['model']} ({best_efficiency['avg_reward']:.3f} avg reward)")
            
    except Exception as e:
        if not quiet:
            print(f"Failed to get performance summary: {e}")


def print_achievement_analysis(db, experiment_ids: Dict[str, str], quiet: bool):
    """Analyze achievement patterns across models."""
    if not quiet:
        print("\n## 🏆 Achievement Analysis")
        print("-" * 30)
    
    try:
        # Get achievement counts by model (simplified approach looking in event_metadata)
        valid_experiment_ids = [eid for eid in experiment_ids.values() if eid != "failed"]
        if not valid_experiment_ids:
            print("No achievement data available")
            return
            
        query = """
        SELECT 
            st.experiment_id,
            COALESCE(
                json_extract(ev.metadata, '$.achievement'),
                json_extract(ev.event_metadata, '$[0].achievement'),
                'generic_achievement'
            ) as achievement,
            'unknown' as difficulty,
            COUNT(*) as achievement_count
        FROM session_traces st
        JOIN events ev ON st.session_id = ev.session_id
        WHERE st.experiment_id IN ({})
            AND ev.event_type = 'runtime'
            AND (
                json_extract(ev.metadata, '$.achievement') IS NOT NULL
                OR (ev.event_metadata IS NOT NULL 
                    AND ev.event_metadata != '[]'
                    AND ev.event_metadata LIKE '%achievement%')
            )
        GROUP BY st.experiment_id, achievement
        ORDER BY achievement_count DESC
        """.format(','.join([f"'{eid}'" for eid in valid_experiment_ids]))
        
        df = db.query_traces(query)
        
        if df.empty:
            print("No achievement data available")
            return
            
        # Map experiment IDs back to model names
        exp_to_model = {v: k for k, v in experiment_ids.items() if v != "failed"}
        df['model'] = df['experiment_id'].map(exp_to_model)
        
        # Pivot table for achievements by model
        pivot = df.pivot_table(index='achievement', columns='model', values='achievement_count', fill_value=0)
        
        if not quiet:
            print("\n### Achievement Counts by Model:")
            print(pivot.to_string())
            
            # Show top achievements
            total_achievements = df.groupby('achievement')['achievement_count'].sum().sort_values(ascending=False)
            print(f"\n### Most Common Achievements:")
            for i, (achievement, count) in enumerate(total_achievements.head(5).items()):
                print(f"{i+1}. {achievement}: {count} times")
        else:
            # Show just the winners
            total_by_model = df.groupby('model')['achievement_count'].sum().sort_values(ascending=False)
            if not total_by_model.empty:
                best_model = total_by_model.index[0]
                print(f"🏆 Most Achievements: {best_model} ({total_by_model.iloc[0]} total)")
            
    except Exception as e:
        if not quiet:
            print(f"Failed to analyze achievements: {e}")


def print_action_analysis(db, experiment_ids: Dict[str, str], quiet: bool):
    """Analyze action patterns and invalid actions."""
    if not quiet:
        print("\n## 🎮 Action Analysis")
        print("-" * 25)
    
    try:
        # Get invalid action rates by model (simplified approach)
        valid_experiment_ids = [eid for eid in experiment_ids.values() if eid != "failed"]
        if not valid_experiment_ids:
            print("No action data available")
            return
            
        query = """
        SELECT 
            st.experiment_id,
            COUNT(*) as total_actions,
            SUM(CASE 
                WHEN COALESCE(
                    CAST(json_extract(ev.metadata, '$.invalid_action') AS BOOLEAN),
                    ev.event_metadata LIKE '%invalid_action%'
                ) THEN 1
                ELSE 0 
            END) as invalid_actions,
            ROUND(100.0 * SUM(CASE 
                WHEN COALESCE(
                    CAST(json_extract(ev.metadata, '$.invalid_action') AS BOOLEAN),
                    ev.event_metadata LIKE '%invalid_action%'
                ) THEN 1
                ELSE 0 
            END) / NULLIF(COUNT(*), 0), 2) as invalid_rate
        FROM session_traces st
        JOIN events ev ON st.session_id = ev.session_id
        WHERE st.experiment_id IN ({})
            AND ev.event_type = 'runtime'
            AND json_extract(ev.metadata, '$.step') IS NOT NULL
        GROUP BY st.experiment_id
        ORDER BY invalid_rate ASC
        """.format(','.join([f"'{eid}'" for eid in valid_experiment_ids]))
        
        df = db.query_traces(query)
        
        if df.empty:
            print("No action data available")
            return
            
        # Map experiment IDs back to model names
        exp_to_model = {v: k for k, v in experiment_ids.items() if v != "failed"}
        df['model'] = df['experiment_id'].map(exp_to_model)
        
        if not quiet:
            print("\n| Model | Total Actions | Invalid Actions | Invalid Rate |")
            print("|-------|---------------|-----------------|--------------|")
            
            for _, row in df.iterrows():
                print(f"| {row['model']:<12} | {int(row['total_actions']):>13} | {int(row['invalid_actions']):>15} | {row['invalid_rate']:>10.1f}% |")
        else:
            # Show best and worst
            if not df.empty and 'invalid_rate' in df.columns:
                valid_df = df[df['invalid_rate'].notna()]
                if not valid_df.empty:
                    best_model = valid_df.loc[valid_df['invalid_rate'].idxmin()]
                    worst_model = valid_df.loc[valid_df['invalid_rate'].idxmax()]
                    print(f"🎯 Most Accurate: {best_model['model']} ({best_model['invalid_rate']:.1f}% invalid)")
                    print(f"❌ Least Accurate: {worst_model['model']} ({worst_model['invalid_rate']:.1f}% invalid)")
            
    except Exception as e:
        if not quiet:
            print(f"Failed to analyze actions: {e}")


def print_efficiency_metrics(db, experiment_ids: Dict[str, str], quiet: bool):
    """Analyze efficiency metrics like tokens and cost."""
    if not quiet:
        print("\n## ⚡ Efficiency Metrics")
        print("-" * 25)
    
    try:
        # Get token usage and cost by model (look for events with LLM data)
        valid_experiment_ids = [eid for eid in experiment_ids.values() if eid != "failed"]
        if not valid_experiment_ids:
            print("No efficiency data available")
            return
            
        query = """
        SELECT 
            st.experiment_id,
            COUNT(*) as llm_calls,
            AVG(ev.prompt_tokens) as avg_prompt_tokens,
            AVG(ev.completion_tokens) as avg_completion_tokens,
            SUM(ev.total_tokens) as total_tokens,
            AVG(ev.latency_ms) as avg_latency_ms,
            SUM(COALESCE(ev.cost, 0)) as total_cost
        FROM session_traces st
        JOIN events ev ON st.session_id = ev.session_id
        WHERE st.experiment_id IN ({})
            AND ev.model_name IS NOT NULL
            AND ev.prompt_tokens IS NOT NULL
        GROUP BY st.experiment_id
        ORDER BY total_cost ASC
        """.format(','.join([f"'{eid}'" for eid in valid_experiment_ids]))
        
        df = db.query_traces(query)
        
        if df.empty:
            print("No efficiency data available")
            return
            
        # Map experiment IDs back to model names
        exp_to_model = {v: k for k, v in experiment_ids.items() if v != "failed"}
        df['model'] = df['experiment_id'].map(exp_to_model)
        
        if not quiet:
            print("\n| Model | LLM Calls | Avg Prompt | Avg Completion | Total Tokens | Avg Latency | Total Cost |")
            print("|-------|-----------|------------|----------------|--------------|-------------|------------|")
            
            for _, row in df.iterrows():
                cost = row['total_cost'] if pd.notna(row['total_cost']) else 0.0
                latency = row['avg_latency_ms'] if pd.notna(row['avg_latency_ms']) else 0.0
                prompt_tokens = row['avg_prompt_tokens'] if pd.notna(row['avg_prompt_tokens']) else 0.0
                completion_tokens = row['avg_completion_tokens'] if pd.notna(row['avg_completion_tokens']) else 0.0
                total_tokens = row['total_tokens'] if pd.notna(row['total_tokens']) else 0
                llm_calls = row['llm_calls'] if pd.notna(row['llm_calls']) else 0
                print(f"| {row['model']:<8} | {int(llm_calls):>9} | {prompt_tokens:>10.0f} | {completion_tokens:>14.0f} | {int(total_tokens):>12} | {latency:>9.0f}ms | ${cost:>9.4f} |")
        else:
            # Show most efficient
            if 'total_cost' in df.columns and not df['total_cost'].isna().all():
                valid_cost_df = df[df['total_cost'].notna() & (df['total_cost'] > 0)]
                if not valid_cost_df.empty:
                    cheapest = valid_cost_df.loc[valid_cost_df['total_cost'].idxmin()]
                    print(f"💰 Most Cost-Efficient: {cheapest['model']} (${cheapest['total_cost']:.4f})")
                
            if 'avg_latency_ms' in df.columns and not df['avg_latency_ms'].isna().all():
                valid_latency_df = df[df['avg_latency_ms'].notna() & (df['avg_latency_ms'] > 0)]
                if not valid_latency_df.empty:
                    fastest = valid_latency_df.loc[valid_latency_df['avg_latency_ms'].idxmin()]
                    print(f"🚀 Fastest: {fastest['model']} ({fastest['avg_latency_ms']:.0f}ms avg)")
            
    except Exception as e:
        if not quiet:
            print(f"Failed to analyze efficiency: {e}")


def print_error_analysis(db, experiment_ids: Dict[str, str], quiet: bool):
    """Analyze error patterns and failure modes."""
    if not quiet:
        print("\n## 🔍 Error Analysis")
        print("-" * 20)
    
    try:
        # Look for termination patterns by checking if episodes completed all steps
        valid_experiment_ids = [eid for eid in experiment_ids.values() if eid != "failed"]
        if not valid_experiment_ids:
            if not quiet:
                print("No error data available")
            return
            
        query = """
        SELECT 
            st.experiment_id,
            CASE 
                WHEN st.num_timesteps < 100 THEN 'early_termination'
                WHEN st.num_timesteps >= 100 THEN 'max_steps_reached'
                ELSE 'unknown'
            END as termination_reason,
            COUNT(*) as episode_count
        FROM session_traces st
        WHERE st.experiment_id IN ({})
        GROUP BY st.experiment_id, termination_reason
        ORDER BY episode_count DESC
        """.format(','.join([f"'{eid}'" for eid in valid_experiment_ids]))
        
        df = db.query_traces(query)
        
        if not df.empty:
            # Map experiment IDs back to model names
            exp_to_model = {v: k for k, v in experiment_ids.items() if v != "failed"}
            df['model'] = df['experiment_id'].map(exp_to_model)
            
            if not quiet:
                print("\n### Episode Termination Reasons:")
                pivot = df.pivot_table(index='termination_reason', columns='model', values='episode_count', fill_value=0)
                print(pivot.to_string())
            else:
                # Show most common termination reason
                most_common = df.groupby('termination_reason')['episode_count'].sum().sort_values(ascending=False)
                if not most_common.empty:
                    print(f"🔚 Most Common Termination: {most_common.index[0]} ({most_common.iloc[0]} episodes)")
        
    except Exception as e:
        if not quiet:
            print(f"Failed to analyze errors: {e}")


async def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Run Crafter rollouts for multiple models and compare performance"
    )
    parser.add_argument("--episodes", type=int, default=10, help="Episodes per model")
    parser.add_argument("--max-turns", type=int, default=100, help="Max turns per episode")
    parser.add_argument("--models", nargs="+", default=MODELS_TO_TEST, 
                       help="Models to test")
    parser.add_argument("--database", default=DATABASE_PATH, help="Database path")
    parser.add_argument("--service-url", default=CRAFTER_SERVICE_URL, 
                       help="Crafter service URL")
    parser.add_argument("--concurrent-models", action="store_true", 
                       help="Run models concurrently (default: sequential)")
    parser.add_argument("--max-concurrent-models", type=int, default=3,
                       help="Maximum number of models to run concurrently")
    parser.add_argument("--quiet", action="store_true", 
                       help="Suppress verbose output and only show results")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ExperimentConfig()
    config.num_episodes = args.episodes
    config.max_turns = args.max_turns
    config.database_path = args.database
    config.crafter_service_url = args.service_url
    config.quiet = args.quiet
    
    # Suppress all noisy third-party logging if in quiet mode
    if config.quiet:
        import logging
        # Suppress HTTP and API client logging
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("google_genai").setLevel(logging.WARNING)
        logging.getLogger("google_genai.models").setLevel(logging.WARNING)
        logging.getLogger("openai").setLevel(logging.WARNING)
        logging.getLogger("anthropic").setLevel(logging.WARNING)
        # Suppress DuckDB and tracing logging
        logging.getLogger("synth_ai.tracing_v2.duckdb").setLevel(logging.WARNING)
        logging.getLogger("synth_ai.tracing_v2").setLevel(logging.WARNING)
        # Set root logger to WARNING to catch any other noise
        logging.getLogger().setLevel(logging.WARNING)
    
    # Create trace directory
    os.makedirs(config.v2_trace_dir, exist_ok=True)
    
    # Clear global sessions collection for fresh start
    _SESSIONS.clear()
    
    if not config.quiet:
        print(f"🚀 STARTING MULTI-MODEL CRAFTER EVALUATION")
        print(f"   Models: {args.models}")
        print(f"   Episodes per model: {config.num_episodes}")
        print(f"   Max turns per episode: {config.max_turns}")
        print(f"   Database: {config.database_path}")
        print(f"   Service URL: {config.crafter_service_url}")
        print(f"   Concurrent models: {args.concurrent_models}")
        if args.concurrent_models:
            print(f"   Max concurrent models: {args.max_concurrent_models}")
    
    # Run experiments for each model
    all_results = {}
    experiment_ids = {}
    
    if args.concurrent_models:
        # Run models concurrently with semaphore to limit concurrency
        semaphore = asyncio.Semaphore(args.max_concurrent_models)
        
        async def run_model_with_semaphore(model_name: str):
            async with semaphore:
                try:
                    return model_name, await run_experiment_for_model(model_name, config)
                except Exception as e:
                    print(f"❌ Failed to run experiment for {model_name}: {e}")
                    import traceback
                    traceback.print_exc()
                    return model_name, ("failed", [])
        
        # Create tasks for all models
        model_tasks = [run_model_with_semaphore(model_name) for model_name in args.models]
        
        if not config.quiet:
            print(f"🔄 Running up to {args.max_concurrent_models} models concurrently...")
        
        # Run all model experiments concurrently
        with tqdm(total=len(args.models), desc="Models Completed") as pbar:
            for coro in asyncio.as_completed(model_tasks):
                model_name, (experiment_id, results) = await coro
                all_results[model_name] = results
                experiment_ids[model_name] = experiment_id
                pbar.update(1)
    else:
        # Run models sequentially (original behavior)
        for model_name in args.models:
            try:
                experiment_id, results = await run_experiment_for_model(model_name, config)
                all_results[model_name] = results
                experiment_ids[model_name] = experiment_id
            except Exception as e:
                print(f"❌ Failed to run experiment for {model_name}: {e}")
                import traceback
                traceback.print_exc()
                all_results[model_name] = []
                experiment_ids[model_name] = "failed"
    
    # Now do bulk upload of all collected sessions in single transaction
    if not config.quiet:
        print("📤 Uploading all session traces to database...")
        print(f"📊 Found {len(_SESSIONS)} sessions to upload")
    
    # DEBUG: Check for duplicate session IDs in our collection
    session_ids = list(_SESSIONS.keys())
    unique_ids = set(session_ids)
    if len(session_ids) != len(unique_ids):
        duplicates = len(session_ids) - len(unique_ids)
        print(f"🚨 FOUND {duplicates} DUPLICATE SESSION IDs IN COLLECTION!")
        from collections import Counter
        id_counts = Counter(session_ids)
        for session_id, count in id_counts.items():
            if count > 1:
                print(f"   - {session_id}: {count} times")
    
    # First check what's already in the database
    with DuckDBTraceManager(config.database_path) as db:
        existing_sessions = db.conn.execute("SELECT session_id FROM session_traces").fetchall()
        existing_ids = {row[0] for row in existing_sessions}
        print(f"🔍 Database already contains {len(existing_ids)} sessions")
        
        # Check for conflicts
        conflicts = set(_SESSIONS.keys()) & existing_ids
        if conflicts:
            print(f"⚠️  Found {len(conflicts)} conflicting session IDs in database already!")
            for conflict_id in list(conflicts)[:5]:  # Show first 5
                print(f"   - {conflict_id}")
                # Get details about the existing session
                existing = db.conn.execute(
                    "SELECT session_id, experiment_id, num_timesteps, created_at FROM session_traces WHERE session_id = ?",
                    [conflict_id]
                ).fetchone()
                if existing:
                    print(f"     Existing: session_id={existing[0]}, experiment_id={existing[1]}, timesteps={existing[2]}, created={existing[3]}")
        
        # Also check for duplicates within our own collection
        session_ids = list(_SESSIONS.keys())
        unique_ids = set(session_ids)
        if len(session_ids) != len(unique_ids):
            duplicates = len(session_ids) - len(unique_ids)
            print(f"🚨 FOUND {duplicates} DUPLICATE SESSION IDs IN OUR COLLECTION!")
            from collections import Counter
            id_counts = Counter(session_ids)
            for session_id, count in id_counts.items():
                if count > 1:
                    print(f"   - {session_id}: {count} times")
                    # Show the different experiment_ids for this session_id
                    experiment_ids_for_session = [exp_id for exp_id, _ in _SESSIONS.values() if exp_id == session_id]
                    print(f"     Experiment IDs: {experiment_ids_for_session}")
    
    if _SESSIONS:
        with DuckDBTraceManager(config.database_path) as db:
            uploaded_count = 0
            skipped_count = 0
            
            # Process each session individually to get better error reporting
            for session_id, (experiment_id, trace) in _SESSIONS.items():
                try:
                    # Check if session already exists in database
                    existing = db.conn.execute(
                        "SELECT session_id, experiment_id, num_timesteps FROM session_traces WHERE session_id = ?",
                        [session_id]
                    ).fetchone()
                    
                    if existing:
                        print(f"🔍 SESSION ALREADY EXISTS: {session_id}")
                        print(f"   Existing: session_id={existing[0]}, experiment_id={existing[1]}, timesteps={existing[2]}")
                        print(f"   New: experiment_id={experiment_id}, timesteps={trace.num_timesteps if hasattr(trace, 'num_timesteps') else 'unknown'}")
                        print(f"   Trace object type: {type(trace)}")
                        print(f"   Trace object keys: {trace.__dict__.keys() if hasattr(trace, '__dict__') else 'no __dict__'}")
                        skipped_count += 1
                        continue
                    
                    # Insert session (ON CONFLICT DO NOTHING handles duplicates)
                    db.insert_session_trace(trace)
                    # Update experiment_id
                    db.conn.execute(
                        "UPDATE session_traces SET experiment_id = ? "
                        "WHERE session_id = ? AND (experiment_id IS NULL OR experiment_id = '')",
                        [experiment_id, session_id]
                    )
                    uploaded_count += 1
                except AssertionError as e:
                    # Re-raise assertions to debug the issue
                    print(f"🚨 ASSERTION ERROR for {session_id}: {e}")
                    print(f"   Trace object: {trace}")
                    print(f"   Trace type: {type(trace)}")
                    if hasattr(trace, '__dict__'):
                        print(f"   Trace attributes: {trace.__dict__}")
                    raise
                except Exception as e:
                    print(f"⚠️  Skipped {session_id}: {e}")
                    print(f"   Error type: {type(e).__name__}")
                    print(f"   Trace object type: {type(trace)}")
                    if hasattr(trace, '__dict__'):
                        print(f"   Trace keys: {list(trace.__dict__.keys())}")
                    skipped_count += 1
            
            if not config.quiet:
                print(f"✅ Uploaded {uploaded_count}/{len(_SESSIONS)} sessions to database")
                if skipped_count > 0:
                    print(f"⚠️  Skipped {skipped_count} sessions due to errors")
    else:
        if not config.quiet:
            print("⚠️  No sessions to upload")
    
    # Print comprehensive results
    if not config.quiet:
        print_results_summary(all_results, experiment_ids)
    
    # Generate comprehensive DuckDB analytics
    print_comprehensive_model_analytics(config.database_path, experiment_ids, config.quiet)
    
    # Save results to file
    results_file = Path(config.v2_trace_dir) / f"multi_model_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(results_file, "w") as f:
        json.dump({
            "experiment_ids": experiment_ids,
            "all_results": all_results,
            "config": {
                "models": args.models,
                "episodes": config.num_episodes,
                "max_turns": config.max_turns,
                "timestamp": datetime.now().isoformat()
            },
            "analysis": {
                "performance": analyze_performance_metrics(all_results),
                "invalid_actions": analyze_invalid_actions(all_results),
                "achievements": analyze_achievements_by_step(all_results)
            }
        }, f, indent=2)
    
    if not config.quiet:
        print(f"\n💾 Results saved to {results_file}")
        print(f"📊 Database available at {config.database_path}")


if __name__ == "__main__":
    asyncio.run(main())
