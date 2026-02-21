"""
Desktop Actions Tool
Executes mouse and keyboard actions on the desktop using pyautogui
"""

import time
import logging
from typing import Any, Dict, Optional, List
from enum import Enum
import pyautogui

logger = logging.getLogger(__name__)

# Enable fail-safe: move mouse to top-left corner to abort
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1  # Pause between actions


class ActionType(str, Enum):
    """Supported action types"""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    TYPE = "type"
    HOTKEY = "hotkey"
    SCROLL = "scroll"
    WAIT = "wait"
    MOVE = "move"
    DRAG = "drag"


class DesktopActionError(Exception):
    """Raised when action execution fails"""
    pass


class DesktopActions:
    """Handles desktop automation actions"""
    
    def __init__(self, safe_mode: bool = True):
        """
        Initialize desktop actions
        
        Args:
            safe_mode: If True, adds delays and safety checks
        """
        self.safe_mode = safe_mode
        self.action_history = []
    
    def click(
        self,
        x: int,
        y: int,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.1
    ) -> Dict[str, Any]:
        """
        Click at specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: 'left', 'right', or 'middle'
            clicks: Number of clicks
            interval: Interval between clicks
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.2)
            
            pyautogui.click(x, y, clicks=clicks, interval=interval, button=button)
            
            result = {
                "action": ActionType.CLICK,
                "x": x,
                "y": y,
                "button": button,
                "clicks": clicks,
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Clicked at ({x}, {y}) with {button} button")
            return result
        
        except Exception as e:
            logger.error(f"Click action failed: {str(e)}")
            raise DesktopActionError(f"Click failed at ({x}, {y}): {str(e)}")
    
    def double_click(self, x: int, y: int) -> Dict[str, Any]:
        """Double click at specified coordinates"""
        return self.click(x, y, clicks=2, interval=0.1)
    
    def right_click(self, x: int, y: int) -> Dict[str, Any]:
        """Right click at specified coordinates"""
        return self.click(x, y, button="right")
    
    def type(self, text: str, interval: float = 0.05) -> Dict[str, Any]:
        """
        Type text
        
        Args:
            text: Text to type
            interval: Interval between keystrokes
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.2)
            
            pyautogui.typewrite(text, interval=interval)
            
            result = {
                "action": ActionType.TYPE,
                "text": text[:50] + "..." if len(text) > 50 else text,  # Truncate for logging
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Typed: {text[:50]}")
            return result
        
        except Exception as e:
            logger.error(f"Type action failed: {str(e)}")
            raise DesktopActionError(f"Type failed: {str(e)}")
    
    def write(self, text: str, interval: float = 0.05) -> Dict[str, Any]:
        """
        Write text using keyboard (supports special characters)
        
        Args:
            text: Text to write
            interval: Interval between keystrokes
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.2)
            
            pyautogui.write(text, interval=interval)
            
            result = {
                "action": ActionType.TYPE,
                "text": text[:50] + "..." if len(text) > 50 else text,
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Wrote: {text[:50]}")
            return result
        
        except Exception as e:
            logger.error(f"Write action failed: {str(e)}")
            raise DesktopActionError(f"Write failed: {str(e)}")
    
    def hotkey(self, *keys: str) -> Dict[str, Any]:
        """
        Press hotkey combination
        
        Args:
            *keys: Keys to press (e.g., 'ctrl', 'a')
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.2)
            
            pyautogui.hotkey(*keys)
            
            result = {
                "action": ActionType.HOTKEY,
                "keys": list(keys),
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Hotkey pressed: {'+'.join(keys)}")
            return result
        
        except Exception as e:
            logger.error(f"Hotkey action failed: {str(e)}")
            raise DesktopActionError(f"Hotkey failed: {str(e)}")
    
    def scroll(
        self,
        x: int,
        y: int,
        amount: int = 3,
        direction: str = "down"
    ) -> Dict[str, Any]:
        """
        Scroll at specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            amount: Number of scroll units
            direction: 'up' or 'down'
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.2)
            
            # Move to position first
            pyautogui.moveTo(x, y)
            
            # Scroll (positive = up, negative = down)
            scroll_amount = amount if direction.lower() == "up" else -amount
            pyautogui.scroll(scroll_amount)
            
            result = {
                "action": ActionType.SCROLL,
                "x": x,
                "y": y,
                "amount": amount,
                "direction": direction,
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Scrolled {direction} by {amount} units at ({x}, {y})")
            return result
        
        except Exception as e:
            logger.error(f"Scroll action failed: {str(e)}")
            raise DesktopActionError(f"Scroll failed: {str(e)}")
    
    def wait(self, seconds: float) -> Dict[str, Any]:
        """
        Wait for specified seconds
        
        Args:
            seconds: Seconds to wait
        
        Returns:
            Action result dict
        """
        try:
            time.sleep(seconds)
            
            result = {
                "action": ActionType.WAIT,
                "seconds": seconds,
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Waited {seconds} seconds")
            return result
        
        except Exception as e:
            logger.error(f"Wait action failed: {str(e)}")
            raise DesktopActionError(f"Wait failed: {str(e)}")
    
    def move(self, x: int, y: int, duration: float = 0.5) -> Dict[str, Any]:
        """
        Move mouse to coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Duration of movement in seconds
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.1)
            
            pyautogui.moveTo(x, y, duration=duration)
            
            result = {
                "action": ActionType.MOVE,
                "x": x,
                "y": y,
                "duration": duration,
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Moved to ({x}, {y})")
            return result
        
        except Exception as e:
            logger.error(f"Move action failed: {str(e)}")
            raise DesktopActionError(f"Move failed: {str(e)}")
    
    def drag(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        duration: float = 0.5
    ) -> Dict[str, Any]:
        """
        Drag from one position to another
        
        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate
            y2: Ending Y coordinate
            duration: Duration of drag in seconds
        
        Returns:
            Action result dict
        """
        try:
            if self.safe_mode:
                time.sleep(0.2)
            
            pyautogui.moveTo(x1, y1)
            pyautogui.drag(x2 - x1, y2 - y1, duration=duration)
            
            result = {
                "action": ActionType.DRAG,
                "from": {"x": x1, "y": y1},
                "to": {"x": x2, "y": y2},
                "duration": duration,
                "success": True,
                "timestamp": time.time()
            }
            
            self.action_history.append(result)
            logger.info(f"Dragged from ({x1}, {y1}) to ({x2}, {y2})")
            return result
        
        except Exception as e:
            logger.error(f"Drag action failed: {str(e)}")
            raise DesktopActionError(f"Drag failed: {str(e)}")
    
    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action from dictionary specification
        
        Args:
            action: Action dict with 'action' key and parameters
        
        Returns:
            Action result dict
        """
        action_type = action.get("action")
        args = action.get("args", {})
        
        try:
            if action_type == ActionType.CLICK:
                return self.click(**args)
            elif action_type == ActionType.DOUBLE_CLICK:
                return self.double_click(**args)
            elif action_type == ActionType.RIGHT_CLICK:
                return self.right_click(**args)
            elif action_type == ActionType.TYPE:
                return self.type(**args)
            elif action_type == ActionType.WRITE:
                return self.write(**args)
            elif action_type == ActionType.HOTKEY:
                return self.hotkey(*args.get("keys", []))
            elif action_type == ActionType.SCROLL:
                return self.scroll(**args)
            elif action_type == ActionType.WAIT:
                return self.wait(**args)
            elif action_type == ActionType.MOVE:
                return self.move(**args)
            elif action_type == ActionType.DRAG:
                return self.drag(**args)
            else:
                raise ValueError(f"Unknown action type: {action_type}")
        
        except Exception as e:
            logger.error(f"Failed to execute action: {str(e)}")
            raise DesktopActionError(f"Action execution failed: {str(e)}")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get action history"""
        return self.action_history
    
    def clear_history(self) -> None:
        """Clear action history"""
        self.action_history = []


# Global instance
_desktop_actions = None


def get_desktop_actions() -> DesktopActions:
    """Get or create global DesktopActions instance"""
    global _desktop_actions
    if _desktop_actions is None:
        _desktop_actions = DesktopActions(safe_mode=True)
    return _desktop_actions
