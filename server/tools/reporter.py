"""
Reporter Tool
Generates comprehensive Markdown reports with evidence and logs
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExecutionStep:
    \"\"\"Single execution step with evidence\"\"\"
    step_id: int
    action_type: str
    description: str
    before_screenshot: Optional[str] = None
    after_screenshot: Optional[str] = None
    success: bool = False
    duration: float = 0.0
    error_message: Optional[str] = None
    validation_result: Optional[Dict[str, Any]] = None


class ReporterError(Exception):
    \"\"\"Raised when report generation fails\"\"\"
    pass


class Reporter:
    \"\"\"Generates comprehensive execution reports\"\"\"
    
    def __init__(self, artifacts_dir: str = "artifacts/reports"):
        self.artifacts_dir = Path(artifacts_dir)
        self.artifacts_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(
        self,
        task_id: str,
        task_goal: str,
        steps: List[ExecutionStep],
        total_duration: float,
        success: bool,
        error_summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        \"\"\"
        Generate comprehensive Markdown report
        
        Args:
            task_id: Unique task identifier
            task_goal: Original task goal
            steps: List of execution steps
            total_duration: Total execution time
            success: Whether task completed successfully
            error_summary: Summary of any errors
            metadata: Additional metadata
        
        Returns:
            Path to generated report file
        
        Raises:
            ReporterError: If report generation fails
        \"\"\"
        try:
            # Generate report content
            report_content = self._build_report(
                task_id=task_id,
                task_goal=task_goal,
                steps=steps,
                total_duration=total_duration,
                success=success,
                error_summary=error_summary,
                metadata=metadata
            )
            
            # Save report
            report_path = self.artifacts_dir / f\"{task_id}_report.md\"
            report_path.write_text(report_content, encoding='utf-8')
            
            logger.info(f\"Report generated: {report_path}\")
            return str(report_path)
        
        except Exception as e:
            logger.error(f\"Report generation failed: {str(e)}\")
            raise ReporterError(f\"Failed to generate report: {str(e)}\")
    
    def _build_report(
        self,
        task_id: str,
        task_goal: str,
        steps: List[ExecutionStep],
        total_duration: float,
        success: bool,
        error_summary: Optional[str],
        metadata: Optional[Dict[str, Any]]
    ) -> str:
        \"\"\"Build report content\"\"\"
        
        timestamp = datetime.now().isoformat()
        status = \"✅ SUCCESS\" if success else \"❌ FAILED\"
        
        # Header
        report = f\"\"\"# Gemini Screen Navigator - Execution Report

**Status:** {status}
**Task ID:** `{task_id}`
**Timestamp:** {timestamp}
**Duration:** {total_duration:.2f} seconds

---

## Task Goal

{task_goal}

---

## Execution Summary

- **Total Steps:** {len(steps)}
- **Successful Steps:** {sum(1 for s in steps if s.success)}
- **Failed Steps:** {sum(1 for s in steps if not s.success)}
- **Success Rate:** {(sum(1 for s in steps if s.success) / len(steps) * 100):.1f}%
- **Total Duration:** {total_duration:.2f} seconds

\"\"\"
        
        # Error summary
        if error_summary:
            report += f\"\"\"## Errors

{error_summary}

---

\"\"\"
        
        # Metadata
        if metadata:
            report += \"\"\"## Metadata

| Key | Value |
|-----|-------|
\"\"\"
            for key, value in metadata.items():
                report += f\"| {key} | {value} |\\n\"
            report += \"\\n---\\n\\n\"
        
        # Steps detail
        report += \"\"\"## Execution Steps

\"\"\"
        
        for step in steps:
            status_icon = \"✅\" if step.success else \"❌\"
            report += f\"\"\"### {status_icon} Step {step.step_id}: {step.action_type}

**Description:** {step.description}
**Duration:** {step.duration:.2f}s
**Status:** {'Success' if step.success else 'Failed'}

\"\"\"
            
            # Error message
            if step.error_message:
                report += f\"**Error:** {step.error_message}\\n\\n\"
            
            # Validation result
            if step.validation_result:
                report += \"**Validation Result:**\\n\"
                for key, value in step.validation_result.items():
                    report += f\"- {key}: {value}\\n\"
                report += \"\\n\"
            
            # Screenshots
            if step.before_screenshot or step.after_screenshot:
                report += \"**Evidence:**\\n\\n\"
                
                if step.before_screenshot:
                    report += f\"**Before:**\\n![Before]({step.before_screenshot})\\n\\n\"
                
                if step.after_screenshot:
                    report += f\"**After:**\\n![After]({step.after_screenshot})\\n\\n\"
            
            report += \"---\\n\\n\"
        
        # Summary
        report += \"\"\"## Summary

\"\"\"
        
        if success:
            report += f\"\"\"The task was completed successfully in {total_duration:.2f} seconds.
All steps were executed as planned and validated.

\"\"\"
        else:
            report += f\"\"\"The task failed after {total_duration:.2f} seconds.
Please review the error messages and evidence above.

\"\"\"
        
        report += f\"\"\"---

*Report generated by Gemini Screen Navigator*
*Powered by Google Gemini API*
\"\"\"
        
        return report
    
    def generate_json_report(
        self,
        task_id: str,
        task_goal: str,
        steps: List[ExecutionStep],
        total_duration: float,
        success: bool,
        error_summary: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        \"\"\"
        Generate JSON report
        
        Args:
            Same as generate_report
        
        Returns:
            Path to generated JSON report
        \"\"\"
        try:
            import json
            
            # Convert steps to dict
            steps_data = []
            for step in steps:
                steps_data.append({
                    \"step_id\": step.step_id,
                    \"action_type\": step.action_type,
                    \"description\": step.description,
                    \"before_screenshot\": step.before_screenshot,
                    \"after_screenshot\": step.after_screenshot,
                    \"success\": step.success,
                    \"duration\": step.duration,
                    \"error_message\": step.error_message,
                    \"validation_result\": step.validation_result
                })
            
            report_data = {
                \"task_id\": task_id,
                \"task_goal\": task_goal,
                \"timestamp\": datetime.now().isoformat(),
                \"success\": success,
                \"total_duration\": total_duration,
                \"total_steps\": len(steps),
                \"successful_steps\": sum(1 for s in steps if s.success),
                \"failed_steps\": sum(1 for s in steps if not s.success),
                \"error_summary\": error_summary,
                \"metadata\": metadata or {},
                \"steps\": steps_data
            }
            
            # Save JSON report
            report_path = self.artifacts_dir / f\"{task_id}_report.json\"
            report_path.write_text(json.dumps(report_data, indent=2), encoding='utf-8')
            
            logger.info(f\"JSON report generated: {report_path}\")
            return str(report_path)
        
        except Exception as e:
            logger.error(f\"JSON report generation failed: {str(e)}\")
            raise ReporterError(f\"Failed to generate JSON report: {str(e)}\")


# Global instance
_reporter = None


def get_reporter() -> Reporter:
    \"\"\"Get or create global Reporter instance\"\"\"
    global _reporter
    if _reporter is None:
        _reporter = Reporter()
    return _reporter
