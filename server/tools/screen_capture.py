"""
Screen Capture Tool
Captures desktop screenshots using mss library
"""

import os
import io
from datetime import datetime
from pathlib import Path
from typing import Optional
import mss
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ScreenCaptureError(Exception):
    """Raised when screen capture fails"""
    pass


class ScreenCapture:
    """Handles desktop screenshot capture and processing"""
    
    def __init__(self, artifacts_dir: str = "artifacts/screenshots"):
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.mss_instance = mss.mss()
    
    def capture_screen(
        self,
        task_id: str,
        step_id: Optional[int] = None,
        quality: int = 85,
        format: str = "jpeg"
    ) -> dict:
        """
        Capture current desktop screenshot
        
        Args:
            task_id: Unique task identifier
            step_id: Optional step number for organizing screenshots
            quality: JPEG quality (1-100), default 85
            format: Image format ('jpeg' or 'png'), default 'jpeg'
        
        Returns:
            dict with keys:
                - path: Local file path
                - url: URL if uploaded to cloud
                - timestamp: Capture timestamp
                - size: File size in bytes
        
        Raises:
            ScreenCaptureError: If capture fails
        """
        try:
            # Create task directory
            task_dir = self.artifacts_dir / task_id
            task_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now()
            if step_id is not None:
                filename = f"step_{step_id:03d}_{timestamp.strftime('%Y%m%d_%H%M%S_%f')[:-3]}.{format}"
            else:
                filename = f"capture_{timestamp.strftime('%Y%m%d_%H%M%S_%f')[:-3]}.{format}"
            
            filepath = task_dir / filename
            
            # Capture all monitors (primary monitor by default)
            with self.mss_instance as sct:
                monitor = sct.monitors[1]  # Primary monitor
                screenshot = sct.grab(monitor)
                
                # Convert to PIL Image
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Save with specified format
                if format.lower() == 'jpeg':
                    img.save(str(filepath), format='JPEG', quality=quality, optimize=True)
                elif format.lower() == 'png':
                    img.save(str(filepath), format='PNG', optimize=True)
                else:
                    raise ValueError(f"Unsupported format: {format}")
            
            # Get file size
            file_size = filepath.stat().st_size
            
            logger.info(f"Screenshot captured: {filepath} ({file_size} bytes)")
            
            return {
                "path": str(filepath),
                "filename": filename,
                "timestamp": timestamp.isoformat(),
                "size": file_size,
                "format": format,
                "task_id": task_id,
                "step_id": step_id
            }
        
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {str(e)}")
            raise ScreenCaptureError(f"Screenshot capture failed: {str(e)}")
    
    def capture_screen_bytes(
        self,
        quality: int = 85,
        format: str = "jpeg"
    ) -> bytes:
        """
        Capture screenshot and return as bytes (for API responses)
        
        Args:
            quality: JPEG quality (1-100)
            format: Image format ('jpeg' or 'png')
        
        Returns:
            Image bytes
        """
        try:
            with self.mss_instance as sct:
                monitor = sct.monitors[1]
                screenshot = sct.grab(monitor)
                img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
                
                # Save to bytes buffer
                buffer = io.BytesIO()
                if format.lower() == 'jpeg':
                    img.save(buffer, format='JPEG', quality=quality, optimize=True)
                elif format.lower() == 'png':
                    img.save(buffer, format='PNG', optimize=True)
                else:
                    raise ValueError(f"Unsupported format: {format}")
                
                return buffer.getvalue()
        
        except Exception as e:
            logger.error(f"Failed to capture screenshot bytes: {str(e)}")
            raise ScreenCaptureError(f"Screenshot capture failed: {str(e)}")
    
    def get_screenshot_path(self, task_id: str, step_id: int) -> Optional[str]:
        """Get path to a specific screenshot"""
        task_dir = self.artifacts_dir / task_id
        if not task_dir.exists():
            return None
        
        # Find screenshot file for this step
        for file in sorted(task_dir.glob(f"step_{step_id:03d}_*")):
            return str(file)
        
        return None
    
    def list_screenshots(self, task_id: str) -> list:
        """List all screenshots for a task"""
        task_dir = self.artifacts_dir / task_id
        if not task_dir.exists():
            return []
        
        screenshots = []
        for file in sorted(task_dir.glob("step_*.jpeg")) + sorted(task_dir.glob("step_*.png")):
            screenshots.append({
                "filename": file.name,
                "path": str(file),
                "size": file.stat().st_size
            })
        
        return screenshots
    
    def cleanup(self, task_id: str) -> bool:
        """Delete all screenshots for a task"""
        try:
            task_dir = self.artifacts_dir / task_id
            if task_dir.exists():
                import shutil
                shutil.rmtree(task_dir)
                logger.info(f"Cleaned up screenshots for task {task_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to cleanup screenshots: {str(e)}")
            return False


# Global instance
_screen_capture = None


def get_screen_capture() -> ScreenCapture:
    """Get or create global ScreenCapture instance"""
    global _screen_capture
    if _screen_capture is None:
        _screen_capture = ScreenCapture()
    return _screen_capture
