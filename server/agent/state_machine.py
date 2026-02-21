"""
Agent State Machine
Manages the Perceive-Plan-Act-Verify execution loop
"""

import logging
import time
import json
from typing import Any, Dict, List, Optional, Tuple
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio

logger = logging.getLogger(__name__)


class TaskState(str, Enum):
    \"\"\"Task execution states\"\"\"
    IDLE = "idle\"
    RUNNING = "running\"
    WAITING_APPROVAL = "waiting_approval\"
    VERIFYING = "verifying\"
    COMPLETED = "completed\"
    FAILED = "failed\"
    PAUSED = "paused\"


@dataclass
class TaskExecution:
    \"\"\"Task execution record\"\"\"
    task_id: str
    goal: str
    state: TaskState
    current_step: int
    total_steps: int
    start_time: float
    end_time: Optional[float] = None
    steps_executed: List[Dict[str, Any]] = None
    errors: List[str] = None
    safety_flags: List[str] = None
    approval_required: bool = False
    approval_pending_step: Optional[int] = None
    
    def __post_init__(self):
        if self.steps_executed is None:
            self.steps_executed = []
        if self.errors is None:
            self.errors = []
        if self.safety_flags is None:
            self.safety_flags = []
    
    @property
    def duration(self) -> float:
        \"\"\"Get execution duration\"\"\"
        end = self.end_time or time.time()
        return end - self.start_time
    
    @property
    def progress(self) -> float:
        \"\"\"Get progress percentage\"\"\"
        if self.total_steps == 0:
            return 0
        return (self.current_step / self.total_steps) * 100


class AgentStateMachine:
    \"\"\"Manages agent execution state and transitions\"\"\"
    
    def __init__(self):
        self.tasks: Dict[str, TaskExecution] = {}
        self.max_retries = 3
    
    def create_task(
        self,
        task_id: str,
        goal: str,
        total_steps: int
    ) -> TaskExecution:
        \"\"\"Create new task\"\"\"
        task = TaskExecution(
            task_id=task_id,
            goal=goal,
            state=TaskState.IDLE,
            current_step=0,
            total_steps=total_steps,
            start_time=time.time()
        )
        self.tasks[task_id] = task
        logger.info(f\"Task created: {task_id}\")
        return task
    
    def start_task(self, task_id: str) -> bool:
        \"\"\"Start task execution\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.state != TaskState.IDLE:
            return False
        
        task.state = TaskState.RUNNING
        logger.info(f\"Task started: {task_id}\")
        return True
    
    def pause_task(self, task_id: str) -> bool:
        \"\"\"Pause task execution\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.state not in [TaskState.RUNNING, TaskState.VERIFYING]:
            return False
        
        task.state = TaskState.PAUSED
        logger.info(f\"Task paused: {task_id}\")
        return True
    
    def resume_task(self, task_id: str) -> bool:
        \"\"\"Resume task execution\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.state != TaskState.PAUSED:
            return False
        
        task.state = TaskState.RUNNING
        logger.info(f\"Task resumed: {task_id}\")
        return True
    
    def request_approval(self, task_id: str, step_id: int) -> bool:
        \"\"\"Request user approval for action\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.state = TaskState.WAITING_APPROVAL
        task.approval_required = True
        task.approval_pending_step = step_id
        logger.info(f\"Approval requested for task {task_id}, step {step_id}\")
        return True
    
    def approve_action(self, task_id: str) -> bool:
        \"\"\"Approve pending action\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.state != TaskState.WAITING_APPROVAL:
            return False
        
        task.state = TaskState.RUNNING
        task.approval_required = False
        logger.info(f\"Action approved for task {task_id}\")
        return True
    
    def reject_action(self, task_id: str, reason: str) -> bool:
        \"\"\"Reject pending action\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if task.state != TaskState.WAITING_APPROVAL:
            return False
        
        task.state = TaskState.FAILED
        task.errors.append(f\"Action rejected by user: {reason}\")
        task.end_time = time.time()
        logger.info(f\"Action rejected for task {task_id}: {reason}\")
        return True
    
    def step_completed(
        self,
        task_id: str,
        step_id: int,
        step_data: Dict[str, Any]
    ) -> bool:
        \"\"\"Mark step as completed\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.current_step = step_id
        task.steps_executed.append(step_data)
        logger.info(f\"Step {step_id} completed for task {task_id}\")
        return True
    
    def step_failed(
        self,
        task_id: str,
        step_id: int,
        error: str,
        retry_count: int = 0
    ) -> Tuple[bool, bool]:
        \"\"\"
        Handle step failure
        
        Returns:
            Tuple of (success, should_retry)
        \"\"\"
        if task_id not in self.tasks:
            return False, False
        
        task = self.tasks[task_id]
        
        if retry_count < self.max_retries:
            logger.warning(f\"Step {step_id} failed, retry {retry_count + 1}/{self.max_retries}\")
            return True, True
        else:
            task.errors.append(f\"Step {step_id} failed after {self.max_retries} retries: {error}\")
            logger.error(f\"Step {step_id} failed permanently: {error}\")
            return False, False
    
    def add_safety_flag(self, task_id: str, flag: str) -> bool:
        \"\"\"Add safety flag to task\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        if flag not in task.safety_flags:
            task.safety_flags.append(flag)
        return True
    
    def complete_task(self, task_id: str, success: bool = True) -> bool:
        \"\"\"Complete task execution\"\"\"
        if task_id not in self.tasks:
            return False
        
        task = self.tasks[task_id]
        task.state = TaskState.COMPLETED if success else TaskState.FAILED
        task.end_time = time.time()
        logger.info(f\"Task completed: {task_id} (success={success})\")
        return True
    
    def get_task(self, task_id: str) -> Optional[TaskExecution]:
        \"\"\"Get task execution record\"\"\"
        return self.tasks.get(task_id)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        \"\"\"Get task status as dict\"\"\"
        task = self.tasks.get(task_id)
        if not task:
            return {}
        
        return {
            \"task_id\": task.task_id,
            \"goal\": task.goal,
            \"state\": task.state.value,
            \"current_step\": task.current_step,
            \"total_steps\": task.total_steps,
            \"progress\": task.progress,
            \"duration\": task.duration,
            \"steps_executed\": len(task.steps_executed),
            \"errors\": task.errors,
            \"safety_flags\": task.safety_flags,
            \"approval_required\": task.approval_required,
            \"approval_pending_step\": task.approval_pending_step
        }
    
    def cleanup_task(self, task_id: str) -> bool:
        \"\"\"Remove task from memory\"\"\"
        if task_id in self.tasks:
            del self.tasks[task_id]
            logger.info(f\"Task cleaned up: {task_id}\")
            return True
        return False
    
    def list_tasks(self, state: Optional[TaskState] = None) -> List[Dict[str, Any]]:
        \"\"\"List all tasks, optionally filtered by state\"\"\"
        tasks = []
        for task in self.tasks.values():
            if state is None or task.state == state:
                tasks.append(self.get_task_status(task.task_id))
        return tasks


# Global instance
_state_machine = None


def get_state_machine() -> AgentStateMachine:
    \"\"\"Get or create global state machine\"\"\"
    global _state_machine
    if _state_machine is None:
        _state_machine = AgentStateMachine()
    return _state_machine
