"""
Safety Checker Tool
Validates actions against safety rules and permission requirements
"""

import logging
import re
from typing import List, Dict, Any, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class SafetyLevel(str, Enum):
    \"\"\"Safety levels for actions\"\"\"
    SAFE = "safe"
    WARNING = "warning\"
    DANGEROUS = "dangerous"
    FORBIDDEN = "forbidden"


class SafetyChecker:
    \"\"\"Validates actions for safety and permission requirements\"\"\"
    
    def __init__(self, require_approval_for_financial: bool = True,
                 require_approval_for_communication: bool = True,
                 require_approval_for_destructive: bool = True):
        \"\"\"
        Initialize safety checker
        
        Args:
            require_approval_for_financial: Require approval for financial actions
            require_approval_for_communication: Require approval for communication
            require_approval_for_destructive: Require approval for destructive actions
        \"\"\"
        self.require_approval_for_financial = require_approval_for_financial
        self.require_approval_for_communication = require_approval_for_communication
        self.require_approval_for_destructive = require_approval_for_destructive
        
        # Define patterns for dangerous actions
        self.financial_keywords = [
            'buy', 'purchase', 'checkout', 'pay', 'payment', 'charge',
            'transaction', 'transfer', 'send money', 'wire', 'refund',
            'subscribe', 'billing', 'credit card', 'debit card', 'bank'
        ]
        
        self.communication_keywords = [
            'send', 'email', 'message', 'sms', 'text', 'post', 'tweet',
            'comment', 'reply', 'share', 'publish', 'upload', 'attach',
            'forward', 'cc', 'bcc', 'mail'
        ]
        
        self.destructive_keywords = [
            'delete', 'remove', 'clear', 'erase', 'destroy', 'drop',
            'truncate', 'format', 'uninstall', 'unlink', 'rm', 'rmdir',
            'empty', 'purge', 'wipe'
        ]
        
        self.account_keywords = [
            'password', 'permission', 'role', 'admin', 'access', 'token',
            'key', 'secret', 'credential', 'auth', 'login', 'logout',
            'sign out', 'change password', 'reset password'
        ]
        
        self.system_keywords = [
            'install', 'uninstall', 'update', 'upgrade', 'downgrade',
            'settings', 'config', 'registry', 'system', 'kernel',
            'driver', 'service', 'daemon', 'process'
        ]
    
    def check_action(
        self,
        action_type: str,
        action_description: str,
        context: str = \"\"
    ) -> Tuple[SafetyLevel, List[str], str]:
        \"\"\"
        Check action for safety issues
        
        Args:
            action_type: Type of action (click, type, etc.)
            action_description: Description of what the action does
            context: Additional context
        
        Returns:
            Tuple of (safety_level, flags, message)
        \"\"\"
        flags = []
        combined_text = f\"{action_description} {context}\".lower()
        
        # Check for financial actions
        if self._contains_keywords(combined_text, self.financial_keywords):
            flags.append(\"financial_action\")
            if self.require_approval_for_financial:
                return SafetyLevel.DANGEROUS, flags, \"Financial transaction detected. Requires user approval.\"
        
        # Check for communication actions
        if self._contains_keywords(combined_text, self.communication_keywords):
            flags.append(\"communication_action\")
            if self.require_approval_for_communication:
                return SafetyLevel.DANGEROUS, flags, \"Communication action detected. Requires user approval.\"
        
        # Check for destructive actions
        if self._contains_keywords(combined_text, self.destructive_keywords):
            flags.append(\"destructive_action\")
            if self.require_approval_for_destructive:
                return SafetyLevel.DANGEROUS, flags, \"Destructive action detected. Requires user approval.\"
        
        # Check for account modifications
        if self._contains_keywords(combined_text, self.account_keywords):
            flags.append(\"account_modification\")
            return SafetyLevel.WARNING, flags, \"Account modification detected. Please verify.\"
        
        # Check for system changes
        if self._contains_keywords(combined_text, self.system_keywords):
            flags.append(\"system_change\")
            return SafetyLevel.WARNING, flags, \"System change detected. Please verify.\"
        
        # No issues found
        return SafetyLevel.SAFE, flags, \"Action appears safe.\"
    
    def check_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Check entire execution plan for safety issues
        
        Args:
            plan: Agent plan dict
        
        Returns:
            Dict with safety analysis
        \"\"\"
        all_flags = []
        dangerous_steps = []
        warnings = []
        
        steps = plan.get(\"steps\", [])
        
        for step in steps:
            step_id = step.get(\"id\")
            action = step.get(\"action\")
            description = step.get(\"thought_short\", \"\")
            
            safety_level, flags, message = self.check_action(
                action,
                description,
                plan.get(\"goal\", \"\")
            )
            
            if flags:
                all_flags.extend(flags)
            
            if safety_level == SafetyLevel.DANGEROUS:
                dangerous_steps.append({
                    \"step_id\": step_id,
                    \"action\": action,
                    \"message\": message,
                    \"flags\": flags
                })
            elif safety_level == SafetyLevel.WARNING:
                warnings.append({
                    \"step_id\": step_id,
                    \"action\": action,
                    \"message\": message,
                    \"flags\": flags
                })
        
        return {
            \"safe\": len(dangerous_steps) == 0,
            \"all_flags\": list(set(all_flags)),
            \"dangerous_steps\": dangerous_steps,
            \"warnings\": warnings,
            \"requires_approval\": len(dangerous_steps) > 0
        }
    
    def _contains_keywords(self, text: str, keywords: List[str]) -> bool:
        \"\"\"Check if text contains any of the keywords\"\"\"
        for keyword in keywords:
            # Use word boundaries to avoid partial matches
            pattern = r'\\b' + re.escape(keyword) + r'\\b'
            if re.search(pattern, text):
                return True
        return False
    
    def get_safety_message(self, flags: List[str]) -> str:
        \"\"\"Get human-readable safety message for flags\"\"\"
        messages = {
            \"financial_action\": \"This action involves a financial transaction.\",
            \"communication_action\": \"This action involves sending a message or communication.\",
            \"destructive_action\": \"This action may delete or destroy data.\",
            \"account_modification\": \"This action modifies account settings or permissions.\",
            \"system_change\": \"This action may change system settings.\"
        }
        
        flag_messages = [messages.get(flag, f\"Unknown flag: {flag}\") for flag in flags]
        return \" \".join(flag_messages)


# Global instance
_safety_checker = None


def get_safety_checker(
    require_approval_for_financial: bool = True,
    require_approval_for_communication: bool = True,
    require_approval_for_destructive: bool = True
) -> SafetyChecker:
    \"\"\"Get or create global SafetyChecker instance\"\"\"
    global _safety_checker
    if _safety_checker is None:
        _safety_checker = SafetyChecker(
            require_approval_for_financial=require_approval_for_financial,
            require_approval_for_communication=require_approval_for_communication,
            require_approval_for_destructive=require_approval_for_destructive
        )
    return _safety_checker
