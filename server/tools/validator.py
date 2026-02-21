"""
Validator Tool
Validates action success by comparing screenshots and analyzing results
"""

import logging
from typing import Any, Dict, Optional
from pathlib import Path
from PIL import Image
import numpy as np

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when validation fails"""
    pass


class Validator:
    \"\"\"Validates action success using image comparison and Gemini analysis\"\"\"
    
    def __init__(self, gemini_brain=None):
        \"\"\"
        Initialize validator
        
        Args:
            gemini_brain: Optional GeminiBrain instance for advanced validation
        \"\"\"
        self.gemini_brain = gemini_brain
    
    def compare_screenshots(
        self,
        before_path: str,
        after_path: str,
        threshold: float = 0.95
    ) -> Dict[str, Any]:
        \"\"\"
        Compare two screenshots for differences
        
        Args:
            before_path: Path to before screenshot
            after_path: Path to after screenshot
            threshold: Similarity threshold (0-1)
        
        Returns:
            Dict with comparison results
        \"\"\"
        try:
            # Load images
            before_img = Image.open(before_path).convert('RGB')
            after_img = Image.open(after_path).convert('RGB')
            
            # Check if images are same size
            if before_img.size != after_img.size:
                return {
                    "similar": False,
                    "similarity": 0.0,
                    "difference_type": "size_mismatch",
                    "before_size": before_img.size,
                    "after_size": after_img.size
                }
            
            # Convert to numpy arrays
            before_array = np.array(before_img)
            after_array = np.array(after_img)
            
            # Calculate difference
            diff = np.abs(before_array.astype(float) - after_array.astype(float))
            
            # Calculate similarity (0-1, where 1 is identical)
            max_diff = 255 * 3  # Max possible difference per pixel
            avg_diff = np.mean(diff) / max_diff
            similarity = 1.0 - avg_diff
            
            # Calculate percentage of changed pixels
            changed_pixels = np.sum(np.any(diff > 30, axis=2)) / (before_array.shape[0] * before_array.shape[1])
            
            result = {
                "similar": similarity >= threshold,
                "similarity": round(similarity, 3),
                "changed_pixels_percent": round(changed_pixels * 100, 2),
                "difference_type": "pixel_change" if changed_pixels > 0.01 else "no_change"
            }
            
            logger.info(f"Screenshot comparison: similarity={result['similarity']}, changed={result['changed_pixels_percent']}%")
            return result
        
        except Exception as e:
            logger.error(f"Screenshot comparison failed: {str(e)}")
            raise ValidationError(f"Comparison failed: {str(e)}")
    
    def validate_with_criteria(
        self,
        before_path: str,
        after_path: str,
        success_criteria: str,
        use_gemini: bool = True
    ) -> Dict[str, Any]:
        \"\"\"
        Validate action success based on criteria
        
        Args:
            before_path: Path to before screenshot
            after_path: Path to after screenshot
            success_criteria: Expected success criteria
            use_gemini: Use Gemini for advanced validation
        
        Returns:
            Validation result dict
        \"\"\"
        try:
            # First, do basic image comparison
            comparison = self.compare_screenshots(before_path, after_path)
            
            # If using Gemini and available, do advanced validation
            if use_gemini and self.gemini_brain:
                gemini_result = self.gemini_brain.validate_action_success(
                    before_path,
                    after_path,
                    success_criteria
                )
                
                return {
                    "success": gemini_result.get("success", False),
                    "confidence": gemini_result.get("confidence", 0),
                    "method": "gemini",
                    "changes": comparison.get("changed_pixels_percent", 0),
                    "reasoning": gemini_result.get("reasoning", ""),
                    "changes_observed": gemini_result.get("changes_observed", "")
                }
            else:
                # Basic validation: success if significant changes detected
                changed_percent = comparison.get("changed_pixels_percent", 0)
                success = changed_percent > 1.0  # More than 1% of pixels changed
                
                return {
                    "success": success,
                    "confidence": 70 if success else 30,
                    "method": "pixel_comparison",
                    "changes": changed_percent,
                    "reasoning": f"{'Significant' if success else 'No significant'} changes detected ({changed_percent}%)",
                    "changes_observed": comparison.get("difference_type", "unknown")
                }
        
        except Exception as e:
            logger.error(f"Validation failed: {str(e)}")
            return {
                "success": False,
                "confidence": 0,
                "method": "error",
                "changes": 0,
                "reasoning": f"Validation error: {str(e)}",
                "changes_observed": "error"
            }
    
    def check_element_presence(
        self,
        screenshot_path: str,
        element_description: str
    ) -> Dict[str, Any]:
        \"\"\"
        Check if a UI element is present in screenshot
        
        Args:
            screenshot_path: Path to screenshot
            element_description: Description of element to find
        
        Returns:
            Dict with presence check result
        \"\"\"
        try:
            if not self.gemini_brain:
                return {
                    "present": False,
                    "confidence": 0,
                    "method": "unavailable",
                    "message": "Gemini Brain not available for element detection"
                }
            
            # Use Gemini to detect element
            with open(screenshot_path, "rb") as f:
                import base64
                image_data = base64.standard_b64encode(f.read()).decode("utf-8")
            
            ext = Path(screenshot_path).suffix.lower()
            mime_type = "image/png" if ext == ".png" else "image/jpeg"
            
            prompt = f\"\"\"Check if this element is visible in the screenshot: {element_description}
            
Respond with JSON:
{{
  "present": true/false,
  "confidence": 0-100,
  "location": "description of where it is or why not found",
  "reasoning": "explanation"
}}

Respond ONLY with valid JSON.\"\"\"
            
            response = self.gemini_brain.model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": image_data
                },
                prompt
            ])
            
            import json
            result = json.loads(response.text.strip())
            result["method"] = "gemini"
            
            return result
        
        except Exception as e:
            logger.error(f"Element presence check failed: {str(e)}")
            return {
                "present": False,
                "confidence": 0,
                "method": "error",
                "location": "unknown",
                "reasoning": str(e)
            }


# Global instance
_validator = None


def get_validator(gemini_brain=None) -> Validator:
    \"\"\"Get or create global Validator instance\"\"\"
    global _validator
    if _validator is None:
        _validator = Validator(gemini_brain)
    return _validator
