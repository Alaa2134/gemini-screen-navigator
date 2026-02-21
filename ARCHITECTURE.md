# Gemini Screen Navigator - Architecture Document

## System Overview

**Gemini Screen Navigator** is an intelligent desktop automation agent that uses Google's Gemini multimodal AI model to perceive, plan, and execute tasks on a computer screen. The system operates in a continuous loop: capturing screenshots, analyzing them with Gemini, planning actions, executing them, and validating results.

## Core Architecture

### 1. High-Level Data Flow

```
User Input (Goal)
    ↓
[Frontend UI] → [FastAPI Backend]
    ↓
[Agent State Machine]
    ├─ Perceive: screen_capture → screenshot
    ├─ Plan: gemini_brain → JSON action plan
    ├─ Act: desktop_actions → execute mouse/keyboard
    ├─ Verify: validator → compare before/after
    └─ Report: reporter → Markdown output
    ↓
[S3 Storage] ← screenshots, logs, reports
    ↓
[Frontend Dashboard] ← live updates, evidence gallery
```

### 2. Component Architecture

#### **Frontend (React + Tailwind)**
- **Task Input Page**: Form to accept user goals and task parameters
- **Live Dashboard**: Real-time execution status with logs and screenshot gallery
- **Report Viewer**: Display final Markdown report with evidence
- **Demo Selector**: Choose pre-configured demo scenarios

#### **Backend (FastAPI + Python)**
- **API Endpoints**:
  - `POST /api/task/start` - Start new task execution
  - `GET /api/task/{task_id}/status` - Get real-time status
  - `GET /api/task/{task_id}/report` - Get final report
  - `POST /api/task/{task_id}/approve` - Approve safety-flagged actions
  - `POST /voice/transcribe` - Convert audio to text (optional)

- **Agent State Machine**: Manages the Perceive-Plan-Act-Verify loop
  - Maintains execution state and history
  - Handles retries with different strategies
  - Enforces safety rules and permissions
  - Generates evidence and logs

#### **Tools (Modular Components)**

1. **screen_capture**: Captures desktop screenshots using `mss` library
   - Input: None
   - Output: PNG image file path
   - Stores in: `artifacts/screenshots/{task_id}/`

2. **desktop_actions**: Executes mouse and keyboard actions
   - Input: Action type (click, type, scroll, hotkey, wait)
   - Output: Success/failure status
   - Supported actions: click(x,y), type(text), scroll(x,y,amount), hotkey(*keys), wait(seconds)

3. **gemini_brain**: Analyzes screenshots and generates action plans
   - Input: Screenshot + task context + previous steps
   - Output: JSON with goal, steps array, next_step_id, safety_flags, notes
   - Uses Gemini 2.0 Flash with vision capabilities

4. **validator**: Verifies action success
   - Input: Before screenshot + after screenshot + expected criteria
   - Output: Success/failure with confidence score
   - Uses Gemini for visual comparison and OCR

5. **reporter**: Generates final Markdown report
   - Input: Task history, screenshots, logs
   - Output: Markdown file with evidence
   - Stores in: `artifacts/reports/{task_id}.md`

### 3. Agent State Machine

The agent operates in a state machine with the following states:

```
IDLE → RUNNING → WAITING_APPROVAL → RUNNING → VERIFYING → COMPLETED/FAILED
```

**State Transitions:**
- `IDLE → RUNNING`: User submits task
- `RUNNING → WAITING_APPROVAL`: Safety flag detected (financial, communication, destructive action)
- `WAITING_APPROVAL → RUNNING`: User approves action
- `RUNNING → VERIFYING`: Action executed
- `VERIFYING → RUNNING`: Verification failed, retry with different strategy
- `VERIFYING → COMPLETED`: All steps successful
- `RUNNING/VERIFYING → FAILED`: Max retries exceeded

### 4. Agent Output JSON Schema

```json
{
  "goal": "Complete user registration on example.com",
  "steps": [
    {
      "id": 1,
      "thought_short": "First, I need to navigate to the registration page",
      "tool": "desktop_actions",
      "action": "click",
      "args": {
        "x": 150,
        "y": 200
      },
      "success_criteria": "Registration form should appear on screen"
    },
    {
      "id": 2,
      "thought_short": "Fill in the email field",
      "tool": "desktop_actions",
      "action": "type",
      "args": {
        "text": "user@example.com"
      },
      "success_criteria": "Email should be visible in the input field"
    }
  ],
  "next_step_id": 1,
  "safety_flags": [],
  "notes_for_user": "Starting task execution. Will proceed step by step."
}
```

### 5. Safety Rules & Permission System

**Forbidden Actions (Require User Approval):**
- Financial transactions (purchases, transfers, payments)
- Communication actions (sending emails, messages, posts)
- Destructive actions (deleting files, clearing data)
- Account modifications (password changes, permission changes)
- System changes (installing software, changing settings)

**Safety Check Implementation:**
1. Gemini analyzes planned actions for safety flags
2. If flag detected, agent pauses and requests user approval
3. User reviews action in UI and approves/rejects
4. Agent continues only after approval

### 6. Execution Loop (Pseudocode)

```python
while task_state != COMPLETED and task_state != FAILED:
    # 1. PERCEIVE: Capture current screen state
    screenshot_before = screen_capture()
    
    # 2. PLAN: Ask Gemini what to do next
    plan = gemini_brain(
        screenshot=screenshot_before,
        task_goal=task.goal,
        execution_history=history
    )
    
    # 3. CHECK SAFETY: Validate planned actions
    if plan.safety_flags:
        task_state = WAITING_APPROVAL
        notify_user(plan.safety_flags)
        wait_for_approval()
    
    # 4. ACT: Execute the action
    for step in plan.steps:
        result = execute_action(step)
        log_action(step, result)
    
    # 5. VERIFY: Check if action succeeded
    screenshot_after = screen_capture()
    validation = validator(
        before=screenshot_before,
        after=screenshot_after,
        criteria=step.success_criteria
    )
    
    if validation.success:
        history.append((step, screenshot_before, screenshot_after, validation))
    else:
        if retry_count < 3:
            retry_count += 1
            # Try different strategy (different click point, scroll, etc.)
        else:
            task_state = FAILED
            break
```

### 7. Storage Architecture

**Local Storage (During Execution):**
- `artifacts/screenshots/{task_id}/` - Before/after screenshots
- `artifacts/logs/{task_id}.log` - Execution logs
- `artifacts/reports/{task_id}.md` - Final report

**S3 Storage (Persistent):**
- `gemini-navigator/tasks/{task_id}/screenshots/` - All screenshots
- `gemini-navigator/tasks/{task_id}/report.md` - Final report
- `gemini-navigator/tasks/{task_id}/metadata.json` - Task metadata

### 8. Multimodal Input Support

**Minimum Requirement (Implemented):**
- Screenshot/screen capture (image)
- Text instructions (task goal)

**Bonus Feature (Optional):**
- Voice input via Google Speech-to-Text API
- Audio file upload and transcription
- Converted to text → task goal

### 9. Error Handling & Retry Strategy

**Retry Strategies (Applied in Order):**
1. **First Retry**: Adjust click coordinates (±50 pixels)
2. **Second Retry**: Add scroll action before clicking
3. **Third Retry**: Wait longer between actions (increase from 1s to 3s)

**Max Retries**: 3 attempts per action
**Fallback**: Report failure with evidence and suggest manual intervention

### 10. Integration with Google Cloud

**Deployment Options:**
- **Google Cloud Run**: Recommended for containerized FastAPI app
- **Google Compute Engine**: Alternative for persistent desktop automation (Windows VM)

**Services Used:**
- Cloud Run: Host FastAPI backend
- Cloud Storage: Store artifacts and reports
- Cloud Logging: Centralized logging
- Cloud IAM: Service account permissions

### 11. Security Considerations

1. **API Authentication**: tRPC with Manus OAuth
2. **Action Validation**: All actions validated before execution
3. **Safety Checks**: Gemini-powered safety analysis
4. **User Approval**: Critical actions require explicit user consent
5. **Audit Trail**: All actions logged with timestamps and evidence
6. **Data Isolation**: Task data stored per user/task ID

### 12. Performance Optimization

- **Screenshot Compression**: JPEG format for faster uploads
- **Parallel Processing**: Gemini analysis while action executes
- **Caching**: Cache similar screenshots to reduce API calls
- **Batch Operations**: Group multiple simple actions into single step
- **Timeout Management**: Set reasonable timeouts for each operation

### 13. Monitoring & Logging

**Logged Events:**
- Task start/completion
- Action execution with timing
- Validation results
- Safety flags and approvals
- Errors and retries
- S3 upload status

**Log Levels:**
- INFO: Normal operation progress
- WARNING: Retries, safety flags
- ERROR: Failed actions, API errors
- DEBUG: Detailed step information

## Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Frontend | React 19, Tailwind CSS 4 | User interface and dashboard |
| Backend | FastAPI, Python 3.11 | API and agent logic |
| Screen Capture | mss | Cross-platform screenshot |
| Desktop Control | pyautogui | Mouse and keyboard automation |
| AI Model | Google Gemini 2.0 Flash | Vision and planning |
| Database | MySQL (Drizzle ORM) | Task history and metadata |
| Storage | Amazon S3 | Persistent artifact storage |
| Containerization | Docker | Cloud deployment |
| Cloud Platform | Google Cloud Run | Production hosting |
| RPC Framework | tRPC | Type-safe API |

## File Structure

```
GeminiScreenNavigator/
├── client/                          # React frontend
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Home.tsx            # Task input form
│   │   │   ├── Dashboard.tsx       # Live execution dashboard
│   │   │   ├── Report.tsx          # Report viewer
│   │   │   └── Demo.tsx            # Demo selector
│   │   ├── components/
│   │   │   ├── TaskForm.tsx
│   │   │   ├── ExecutionLog.tsx
│   │   │   ├── ScreenshotGallery.tsx
│   │   │   └── SafetyApproval.tsx
│   │   ├── App.tsx
│   │   └── index.css               # Brutalist styling
│   └── public/
├── server/
│   ├── routers.ts                  # tRPC procedures
│   ├── db.ts                       # Database queries
│   ├── agent/
│   │   ├── state_machine.py        # Agent orchestration
│   │   ├── executor.py             # Execution loop
│   │   └── schemas.py              # Pydantic models
│   ├── tools/
│   │   ├── screen_capture.py
│   │   ├── desktop_actions.py
│   │   ├── gemini_brain.py
│   │   ├── validator.py
│   │   └── reporter.py
│   ├── utils/
│   │   ├── safety_checker.py
│   │   ├── storage.py
│   │   └── logger.py
│   └── _core/                      # Framework code
├── drizzle/
│   └── schema.ts                   # Database schema
├── artifacts/                      # Local storage (during execution)
│   ├── screenshots/
│   ├── logs/
│   └── reports/
├── Dockerfile                      # Container image
├── docker-compose.yml              # Local development
├── requirements.txt                # Python dependencies
├── README.md                        # Setup and usage guide
├── ARCHITECTURE.md                 # This file
├── DEPLOYMENT.md                   # GCP deployment guide
├── DEMO_SCRIPT.md                  # Video demo script
└── FAQ.md                          # Common questions
```

## Next Steps

1. **Phase 2**: Implement backend tools and agent state machine
2. **Phase 3**: Build React frontend with Brutalist design
3. **Phase 4**: Add multimodal input (voice transcription)
4. **Phase 5**: Deploy to Google Cloud Run
5. **Phase 6**: Create comprehensive documentation and demo video

