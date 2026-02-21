"""
Gemini Brain Tool
Analyzes screenshots and generates action plans using Google's Gemini API
"""

import json
import base64
import logging
from typing import Any, Dict, List, Optional
from pathlib import Path
import google.generativeai as genai
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class ActionStep(BaseModel):
    """Single action step in the plan"""
    id: int
    thought_short: str = Field(description="Brief reasoning for this step")
    tool: str = Field(description="Tool to use: desktop_actions, screen_capture, or validator")
    action: str = Field(description="Action type: click, type, scroll, wait, etc.")
    args: Dict[str, Any] = Field(description="Arguments for the action")
    success_criteria: str = Field(description="How to verify this step succeeded")


class AgentPlan(BaseModel):
    """Complete agent execution plan"""
    goal: str
    steps: List[ActionStep]
    next_step_id: int
    safety_flags: List[str] = Field(default_factory=list)
    notes_for_user: str


class GeminiBrainError(Exception):
    """Raised when Gemini API call fails"""
    pass


class GeminiBrain:
    """Analyzes screenshots and generates action plans using Gemini"""
    
    def __init__(self, api_key: str, model: str = "gemini-2.0-flash"):
        """
        Initialize Gemini Brain
        
        Args:
            api_key: Google Gemini API key
            model: Model name to use
        """
        genai.configure(api_key=api_key)
        self.model_name = model
        self.model = genai.GenerativeModel(model)
    
    def analyze_screenshot(
        self,
        screenshot_path: str,
        task_goal: str,
        execution_history: Optional[List[Dict[str, Any]]] = None,
        context: Optional[str] = None
    ) -> AgentPlan:
        """
        Analyze screenshot and generate next action plan
        
        Args:
            screenshot_path: Path to screenshot image
            task_goal: User's task goal
            execution_history: Previous steps executed
            context: Additional context about the task
        
        Returns:
            AgentPlan with next steps
        
        Raises:
            GeminiBrainError: If analysis fails
        """
        try:
            # Read and encode image
            with open(screenshot_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            # Determine image type from file extension
            ext = Path(screenshot_path).suffix.lower()
            if ext == ".png":
                mime_type = "image/png"
            else:
                mime_type = "image/jpeg"
            
            # Build execution history text
            history_text = ""
            if execution_history:
                history_text = "\n\nPrevious steps executed:\n"
                for i, step in enumerate(execution_history, 1):
                    history_text += f"{i}. {step.get('thought_short', 'N/A')}\n"
                    history_text += f"   Action: {step.get('action', 'N/A')}\n"
                    history_text += f"   Result: {'Success' if step.get('success') else 'Failed'}\n"
            
            # Build context text
            context_text = ""
            if context:
                context_text = f"\n\nAdditional context:\n{context}"
            
            # Create prompt
            prompt = f"""You are an intelligent desktop automation agent. Analyze the current screenshot and generate the next action plan.

TASK GOAL: {task_goal}

{history_text}

{context_text}

INSTRUCTIONS:
1. Analyze the current screen state in the screenshot
2. Determine the next logical action(s) to take
3. Generate a detailed action plan in JSON format
4. Include safety flags for any potentially dangerous actions
5. Provide clear success criteria for each step

SAFETY RULES:
- Flag any financial transactions (purchases, transfers, payments)
- Flag any communication actions (emails, messages, posts)
- Flag any destructive actions (file deletion, data clearing)
- Flag any account modifications (password changes, permissions)
- Flag any system changes (software installation, settings changes)

RESPONSE FORMAT (valid JSON):
{{
  "goal": "Current task goal",
  "steps": [
    {{
      "id": 1,
      "thought_short": "Brief reasoning",
      "tool": "desktop_actions",
      "action": "click",
      "args": {{"x": 100, "y": 200}},
      "success_criteria": "Button should be highlighted"
    }}
  ],
  "next_step_id": 1,
  "safety_flags": [],
  "notes_for_user": "Brief explanation of the plan"
}}

Respond ONLY with valid JSON, no additional text."""
            
            # Call Gemini API
            logger.info(f"Calling Gemini API with model {self.model_name}")
            
            response = self.model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": image_data
                },
                prompt
            ])
            
            # Parse response
            response_text = response.text.strip()
            
            # Try to extract JSON from response
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            # Parse JSON
            plan_dict = json.loads(response_text)
            
            # Convert to AgentPlan
            plan = AgentPlan(
                goal=plan_dict.get("goal", task_goal),
                steps=[ActionStep(**step) for step in plan_dict.get("steps", [])],
                next_step_id=plan_dict.get("next_step_id", 1),
                safety_flags=plan_dict.get("safety_flags", []),
                notes_for_user=plan_dict.get("notes_for_user", "")
            )
            
            logger.info(f"Generated plan with {len(plan.steps)} steps")
            return plan
        
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response as JSON: {str(e)}")
            raise GeminiBrainError(f"Invalid JSON response from Gemini: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini API call failed: {str(e)}")
            raise GeminiBrainError(f"Gemini analysis failed: {str(e)}")
    
    def validate_action_success(
        self,
        before_screenshot: str,
        after_screenshot: str,
        success_criteria: str
    ) -> Dict[str, Any]:
        """
        Validate if an action succeeded by comparing screenshots
        
        Args:
            before_screenshot: Path to screenshot before action
            after_screenshot: Path to screenshot after action
            success_criteria: Expected success criteria
        
        Returns:
            Dict with success status and confidence
        """
        try:
            # Read and encode images
            with open(before_screenshot, "rb") as f:
                before_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            with open(after_screenshot, "rb") as f:
                after_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            # Determine image type
            ext = Path(before_screenshot).suffix.lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            
            # Create validation prompt
            prompt = f"""Compare these two screenshots and determine if the action succeeded.

SUCCESS CRITERIA: {success_criteria}

INSTRUCTIONS:
1. Analyze the differences between the before and after screenshots
2. Determine if the success criteria was met
3. Provide confidence level (0-100)
4. Explain what changed

RESPONSE FORMAT (valid JSON):
{{
  "success": true,
  "confidence": 95,
  "changes_observed": "Description of what changed",
  "reasoning": "Why we believe the action succeeded or failed"
}}

Respond ONLY with valid JSON, no additional text."""
            
            logger.info("Validating action success with Gemini")
            
            response = self.model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": before_data
                },
                {
                    "mime_type": mime_type,
                    "data": after_data
                },
                prompt
            ])
            
            # Parse response
            response_text = response.text.strip()
            
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            logger.info(f"Validation result: {result}")
            return result
        
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {
                "success": False,
                "confidence": 0,
                "changes_observed": "Error during validation",
                "reasoning": str(e)
            }
    
    def extract_text_from_screenshot(self, screenshot_path: str) -> str:
        """
        Extract text from screenshot using OCR
        
        Args:
            screenshot_path: Path to screenshot
        
        Returns:
            Extracted text
        """
        try:
            with open(screenshot_path, "rb") as f:
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            ext = Path(screenshot_path).suffix.lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            
            prompt = "Extract all text visible in this screenshot. Return only the text, no explanations."
            
            response = self.model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": image_data
                },
                prompt
            ])
            
            return response.text.strip()
        
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            return ""


# Global instance
_gemini_brain = None


def get_gemini_brain(api_key: str) -> GeminiBrain:
    """Get or create global GeminiBrain instance"""
    global _gemini_brain
    if _gemini_brain is None:
        _gemini_brain = GeminiBrain(api_key)
    return _gemini_brain
