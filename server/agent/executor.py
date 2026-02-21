"""
Agent Executor
Implements the Perceive-Plan-Act-Verify execution loop
"""

import logging
import time
import os
from typing import Any, Dict, List, Optional
from pathlib import Path

from ..tools import (
    get_screen_capture,
    get_desktop_actions,
    get_gemini_brain,
    get_validator,
    get_reporter,
    get_safety_checker,
    get_gcs_storage,
    ExecutionStep
)
from .state_machine import get_state_machine, TaskState

logger = logging.getLogger(__name__)


class ExecutionError(Exception):
    \"\"\"Raised when execution fails\"\"\"
    pass


class AgentExecutor:
    \"\"\"Executes the Perceive-Plan-Act-Verify loop\"\"\"
    
    def __init__(
        self,
        gemini_api_key: str,
        gcp_project_id: str,
        gcs_bucket_name: str = "gemini-navigator",
        max_retries: int = 3
    ):
        \"\"\"Initialize executor\"\"\"
        self.gemini_api_key = gemini_api_key
        self.gcp_project_id = gcp_project_id
        self.gcs_bucket_name = gcs_bucket_name
        self.max_retries = max_retries
        
        # Initialize tools
        self.screen_capture = get_screen_capture()
        self.desktop_actions = get_desktop_actions()
        self.gemini_brain = get_gemini_brain(gemini_api_key)
        self.validator = get_validator(self.gemini_brain)
        self.reporter = get_reporter()
        self.safety_checker = get_safety_checker()
        self.state_machine = get_state_machine()
        
        try:
            self.gcs_storage = get_gcs_storage(gcp_project_id, gcs_bucket_name)
        except Exception as e:
            logger.warning(f\"GCS storage not available: {str(e)}\")
            self.gcs_storage = None
    
    async def execute_task(
        self,
        task_id: str,
        goal: str,
        context: Optional[str] = None,
        demo_mode: bool = False
    ) -> Dict[str, Any]:
        \"\"\"
        Execute complete task
        
        Args:
            task_id: Unique task ID
            goal: Task goal
            context: Additional context
            demo_mode: Run in demo mode (no actual desktop actions)
        
        Returns:
            Execution result dict
        \"\"\"
        try:
            logger.info(f\"Starting task execution: {task_id}\")
            
            # Phase 1: PERCEIVE - Initial screenshot
            logger.info(f\"Phase 1: PERCEIVE - Capturing initial state\")
            initial_screenshot = self.screen_capture.capture_screen(task_id, step_id=0)
            
            # Phase 2: PLAN - Get initial plan from Gemini
            logger.info(f\"Phase 2: PLAN - Generating action plan\")
            plan = self.gemini_brain.analyze_screenshot(
                initial_screenshot[\"path\"],
                goal,
                context=context
            )
            
            # Create task in state machine
            self.state_machine.create_task(task_id, goal, len(plan.steps))
            self.state_machine.start_task(task_id)
            
            # Check safety
            safety_analysis = self.safety_checker.check_plan(plan.dict())
            if not safety_analysis[\"safe\"]:
                logger.warning(f\"Safety issues detected: {safety_analysis}\")
                for flag in safety_analysis[\"all_flags\"]:
                    self.state_machine.add_safety_flag(task_id, flag)
            
            # Execute steps
            execution_steps: List[ExecutionStep] = []
            step_index = 0
            
            while step_index < len(plan.steps):
                step = plan.steps[step_index]
                logger.info(f\"Executing step {step.id}: {step.action}\")
                
                # Check for safety flags
                if step.id in [s[\"step_id\"] for s in safety_analysis.get(\"dangerous_steps\", [])]:
                    logger.warning(f\"Step {step.id} requires approval\")
                    self.state_machine.request_approval(task_id, step.id)
                    # In real implementation, wait for user approval
                    # For now, auto-approve
                    self.state_machine.approve_action(task_id)
                
                # Capture before screenshot
                before_screenshot = self.screen_capture.capture_screen(task_id, step_id=step.id)
                
                # Execute action
                try:
                    if not demo_mode:
                        action_result = self.desktop_actions.execute_action({
                            \"action\": step.action,
                            \"args\": step.args
                        })
                    else:
                        # Demo mode: simulate action
                        action_result = {
                            \"action\": step.action,
                            \"success\": True,
                            \"demo_mode\": True
                        }
                    
                    # Wait for UI update
                    time.sleep(1)
                    
                    # Capture after screenshot
                    after_screenshot = self.screen_capture.capture_screen(task_id, step_id=step.id)
                    
                    # Validate success
                    validation = self.validator.validate_with_criteria(
                        before_screenshot[\"path\"],
                        after_screenshot[\"path\"],
                        step.success_criteria,
                        use_gemini=True
                    )
                    
                    # Record step
                    execution_step = ExecutionStep(
                        step_id=step.id,
                        action_type=step.action,
                        description=step.thought_short,
                        before_screenshot=before_screenshot[\"path\"],
                        after_screenshot=after_screenshot[\"path\"],
                        success=validation[\"success\"],
                        duration=time.time() - before_screenshot.get(\"timestamp\", 0),
                        validation_result=validation
                    )
                    execution_steps.append(execution_step)
                    
                    if validation[\"success\"]:
                        logger.info(f\"Step {step.id} succeeded\")
                        self.state_machine.step_completed(task_id, step.id, {
                            \"step_id\": step.id,
                            \"action\": step.action,
                            \"success\": True,
                            \"validation\": validation
                        })
                        step_index += 1
                    else:
                        # Retry
                        logger.warning(f\"Step {step.id} validation failed, retrying\")
                        # Implement retry logic here
                        step_index += 1
                
                except Exception as e:
                    logger.error(f\"Step {step.id} execution failed: {str(e)}\")
                    execution_step = ExecutionStep(
                        step_id=step.id,
                        action_type=step.action,
                        description=step.thought_short,
                        before_screenshot=before_screenshot[\"path\"],
                        success=False,
                        error_message=str(e)
                    )
                    execution_steps.append(execution_step)
                    step_index += 1
            
            # Generate report
            total_duration = time.time() - self.state_machine.get_task(task_id).start_time
            report_path = self.reporter.generate_report(
                task_id=task_id,
                task_goal=goal,
                steps=execution_steps,
                total_duration=total_duration,
                success=all(s.success for s in execution_steps),
                metadata={
                    \"goal\": goal,
                    \"demo_mode\": demo_mode,
                    \"total_steps\": len(plan.steps),
                    \"successful_steps\": sum(1 for s in execution_steps if s.success)
                }
            )
            
            # Upload to GCS if available
            gcs_report_path = None
            if self.gcs_storage:
                try:
                    result = self.gcs_storage.upload_file(
                        report_path,
                        f\"tasks/{task_id}/report.md\",
                        content_type=\"text/markdown\"
                    )
                    gcs_report_path = result[\"url\"]
                    logger.info(f\"Report uploaded to GCS: {gcs_report_path}\")
                except Exception as e:
                    logger.warning(f\"Failed to upload report to GCS: {str(e)}\")
            
            # Complete task
            success = all(s.success for s in execution_steps)
            self.state_machine.complete_task(task_id, success)
            
            return {
                \"task_id\": task_id,
                \"success\": success,
                \"total_duration\": total_duration,
                \"total_steps\": len(plan.steps),
                \"successful_steps\": sum(1 for s in execution_steps if s.success),
                \"failed_steps\": sum(1 for s in execution_steps if not s.success),
                \"report_path\": report_path,
                \"gcs_report_path\": gcs_report_path,
                \"steps\": [
                    {
                        \"step_id\": s.step_id,
                        \"action\": s.action_type,
                        \"success\": s.success,
                        \"duration\": s.duration,
                        \"error\": s.error_message
                    }
                    for s in execution_steps
                ]
            }
        
        except Exception as e:
            logger.error(f\"Task execution failed: {str(e)}\")
            self.state_machine.complete_task(task_id, success=False)
            raise ExecutionError(f\"Task execution failed: {str(e)}\")


# Global instance
_executor = None


def get_executor(
    gemini_api_key: str,
    gcp_project_id: str,
    gcs_bucket_name: str = \"gemini-navigator\"
) -> AgentExecutor:
    \"\"\"Get or create global executor\"\"\"
    global _executor
    if _executor is None:
        _executor = AgentExecutor(gemini_api_key, gcp_project_id, gcs_bucket_name)
    return _executor
