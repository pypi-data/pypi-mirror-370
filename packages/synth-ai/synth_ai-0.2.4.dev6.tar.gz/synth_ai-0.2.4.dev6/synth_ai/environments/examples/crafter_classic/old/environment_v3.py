"""CrafterClassicEnvironment — thin wrapper exposing CrafterEngine via StatefulEnvironment API.
Updated to use tracing_v3 with async support.
"""

from __future__ import annotations

from typing import List, Optional, Any, Dict, Union
import dataclasses
import logging
import time
import asyncio

# Import logging configuration to suppress JAX debug messages
from .config_logging import safe_compare

# Import tracing abstractions from v3
from synth_ai.tracing_v3.abstractions import (
    RuntimeEvent,
    SessionEventMessage,
    TimeRecord,
)

logger = logging.getLogger(__name__)

from synth_ai.environments.examples.crafter_classic.engine import (
    CrafterEngine,
    CrafterPrivateState,
    CrafterPublicState,
    CrafterEngineSnapshot,
)
from synth_ai.environments.examples.crafter_classic.taskset import CrafterTaskInstance
from synth_ai.environments.environment.shared_engine import (
    GetObservationCallable,
    InternalObservation,
)
from synth_ai.environments.reproducibility.core import ReproducibleEnvironment
from synth_ai.environments.stateful.core import StatefulEnvironment
from synth_ai.environments.environment.tools import (
    AbstractTool,
    EnvToolCall,
    ToolResult,
    TOOL_REGISTRY,
    register_tool,
)
from pydantic import BaseModel, Field


# --- Tool Definition ---
class CrafterActionInput(BaseModel):
    action: int = Field(..., description="Integer action for the Crafter environment.")


class CrafterInteractTool(AbstractTool):
    name = "interact"
    description = "Performs an action in the Crafter environment."
    call_schema = CrafterActionInput
    result_schema = ToolResult

    def __init__(self, engine: CrafterEngine, session_tracer: Optional[Any] = None):
        self.engine = engine
        self.session_tracer = session_tracer

    async def __call__(self, call: EnvToolCall) -> ToolResult:
        try:
            # Store state before execution
            state_before = {"action_args": call.args}
            
            validated_args = self.call_schema(**call.args)
            action_to_pass = self.engine._validate_action_engine(validated_args.action)
            
            # Execute the engine step
            priv_state, pub_state = await self.engine._step_engine(action_to_pass)
            
            # Store state after execution
            state_after = {
                "engine_result": {
                    "private_state": priv_state,
                    "public_state": pub_state
                }
            }
            
            # Record runtime event for tool execution using v3 async API
            if self.session_tracer and hasattr(self.session_tracer, 'current_session') and self.session_tracer.current_session:
                runtime_event = RuntimeEvent(
                    system_instance_id=f"crafter_engine_{id(self.engine)}",
                    time_record=TimeRecord(
                        event_time=time.time(),
                        message_time=None
                    ),
                    actions=[validated_args.action],
                    metadata={
                        "tool_name": self.name,
                        "state_before": state_before,
                        "state_after": state_after
                    }
                )
                # Use async record_event
                await self.session_tracer.record_event(runtime_event)
            
            # Return formatted result
            return ToolResult(
                status="success",
                feedback={"crafter_action": validated_args.action}
            )
        except ValueError as e:
            return ToolResult(status="failure", feedback={"error": str(e)})
        except Exception as e:
            logger.error(f"CrafterInteractTool error: {e}")
            return ToolResult(status="failure", feedback={"error": str(e)})


# --- Environment Implementation ---
@dataclasses.dataclass
class CrafterClassicEnvironment(StatefulEnvironment):
    """
    Implements the StatefulEnvironment interface for CrafterEngine.
    Updated to support async tracing with v3.
    """
    task_instance: CrafterTaskInstance
    engine: CrafterEngine
    interact_tool: CrafterInteractTool
    session_tracer: Optional[Any] = None

    @classmethod
    def from_task_instance(
        cls,
        task_instance: CrafterTaskInstance,
        seed: Optional[int] = None,
        session_tracer: Optional[Any] = None,
    ) -> "CrafterClassicEnvironment":
        """Create a CrafterClassicEnvironment from a task instance with optional v3 session tracer."""
        engine = CrafterEngine(difficulty=task_instance.difficulty, seed=seed)
        interact_tool = CrafterInteractTool(engine, session_tracer)
        return cls(
            task_instance=task_instance,
            engine=engine,
            interact_tool=interact_tool,
            session_tracer=session_tracer,
        )

    # --- StatefulEnvironment Interface Methods ---
    def get_state(self) -> CrafterEngineSnapshot:
        """Return the entire state (private + public)."""
        return self.engine.get_snapshot()

    def get_observation(self) -> Dict[str, Any]:
        """Return public observation data."""
        return self.engine.get_public_state().to_dict()

    def get_human_readable_observation(self) -> str:
        """Return a human-readable version of the observation."""
        obs = self.get_observation()
        lines = ["=== Crafter Observation ==="]
        
        # Status
        status = obs.get('status', {})
        lines.append(f"Health: {status.get('health', 0)}/9")
        lines.append(f"Food: {status.get('food', 0)}/9")
        lines.append(f"Drink: {status.get('drink', 0)}/9")
        lines.append(f"Energy: {status.get('energy', 0)}/9")
        
        # Inventory
        inv = obs.get('inventory', {})
        inv_items = [f"{k}: {v}" for k, v in inv.items() if v > 0]
        lines.append(f"Inventory: {', '.join(inv_items) if inv_items else 'Empty'}")
        
        # Nearby
        nearby = obs.get('nearby', [])
        lines.append(f"Nearby: {', '.join(nearby) if nearby else 'Nothing'}")
        
        # Achievements
        achievements = obs.get('achievements_status', {})
        unlocked = [k for k, v in achievements.items() if v]
        lines.append(f"Achievements: {len(unlocked)}/{len(achievements)}")
        
        return "\n".join(lines)

    def get_status(self) -> str:
        """Return the environment status."""
        pub_state = self.engine.get_public_state()
        if pub_state.done:
            return "terminated"
        return "running"

    def get_available_tools(self) -> List[AbstractTool]:
        """Return available tools."""
        return [self.interact_tool]

    def set_state(self, state: CrafterEngineSnapshot) -> None:
        """Restore environment to a specific state."""
        self.engine.set_snapshot(state)

    def reset(self, seed: Optional[int] = None) -> None:
        """Reset the environment."""
        if seed is not None:
            self.engine.reset(seed)
        else:
            self.engine.reset()

    def render(self, mode: str = "human") -> Optional[Any]:
        """Render the environment."""
        # The engine doesn't have built-in rendering
        if mode == "human":
            return self.get_human_readable_observation()
        return None

    def get_task_description(self) -> str:
        """Return task description."""
        return self.task_instance.get_task_description()

    def get_goal_description(self) -> str:
        """Return goal description."""
        return self.task_instance.get_goal_description()

    def is_successful(self) -> bool:
        """Check if task goals are met."""
        state = self.get_state()
        return self.task_instance.is_successful(state)

    def get_reward(self) -> float:
        """Get current reward."""
        return self.engine.get_public_state().reward

    def get_info(self) -> Dict[str, Any]:
        """Get additional info."""
        pub_state = self.engine.get_public_state()
        return {
            "done": pub_state.done,
            "truncated": pub_state.truncated,
            "reward": pub_state.reward,
            "achievements": pub_state.achievements_status,
        }


# --- ReproducibleEnvironment Implementation ---
@dataclasses.dataclass
class CrafterClassicReproducibleEnvironment(ReproducibleEnvironment):
    """
    Reproducible wrapper for CrafterClassicEnvironment.
    Updated to support v3 session tracer.
    """
    task_instance: CrafterTaskInstance
    seed: Optional[int] = None
    session_tracer: Optional[Any] = None

    def make_env(self) -> CrafterClassicEnvironment:
        """Create the environment instance."""
        return CrafterClassicEnvironment.from_task_instance(
            self.task_instance, 
            seed=self.seed,
            session_tracer=self.session_tracer
        )

    def get_env_args(self) -> Dict[str, Any]:
        """Return arguments needed to recreate the environment."""
        return {
            "task_instance": self.task_instance,
            "seed": self.seed,
            "session_tracer": self.session_tracer,
        }