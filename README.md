# Gemini Screen Navigator

**AI-Powered Desktop Automation Agent using Google Gemini**

An intelligent agent that automates complex desktop tasks by perceiving, planning, acting, and verifying in real-time. Built for the Google Gemini Live Agent Challenge.

---

## Overview

Gemini Screen Navigator is a sophisticated automation system that combines computer vision, natural language understanding, and desktop control to execute complex tasks autonomously. The agent uses Google's Gemini Pro Vision API to analyze screenshots, generate action plans, execute desktop operations, and verify success—all in a continuous loop.

**Key Features:**

- **Multimodal Intelligence**: Analyzes screenshots using Gemini Pro Vision to understand UI context
- **Autonomous Planning**: Generates step-by-step action plans based on task goals
- **Desktop Control**: Executes mouse clicks, keyboard input, and window management
- **Real-time Verification**: Validates action success by comparing before/after screenshots
- **Safety First**: Detects dangerous operations (financial, destructive, communication) and requests approval
- **Comprehensive Logging**: Records every step with screenshots, logs, and evidence
- **Google Cloud Native**: Deploys on Google Cloud Run with Cloud Storage integration

---

## Architecture

The system follows a **Perceive-Plan-Act-Verify** loop:

```
┌─────────────────────────────────────────────────────────┐
│                    GEMINI NAVIGATOR                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │   PERCEIVE   │
                    │ Capture      │
                    │ Screenshot   │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    PLAN      │
                    │ Gemini Brain │
                    │ Analyze UI   │
                    │ Generate     │
                    │ Actions      │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │     ACT      │
                    │ Execute      │
                    │ Desktop      │
                    │ Commands     │
                    └──────────────┘
                           │
                           ▼
                    ┌──────────────┐
                    │    VERIFY    │
                    │ Compare      │
                    │ Screenshots  │
                    │ Validate     │
                    └──────────────┘
                           │
                           ▼
                    Success? Continue Loop
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | React 19 + Tailwind CSS 4 | Web interface with Brutalist design |
| **Backend** | Express 4 + tRPC 11 | API layer with type-safe procedures |
| **Database** | MySQL/TiDB + Drizzle ORM | Task history and user data |
| **AI/ML** | Google Gemini Pro Vision | Screenshot analysis and planning |
| **Desktop Automation** | PyAutoGUI + MSS | Screen capture and action execution |
| **Storage** | Google Cloud Storage | Screenshot and report storage |
| **Deployment** | Google Cloud Run | Serverless container hosting |

---

## Installation

### Prerequisites

- **Node.js** 22+ with pnpm
- **Python** 3.11+
- **Google Cloud Project** with Gemini API enabled
- **Google Cloud Storage Bucket** for artifacts
- **MySQL/TiDB Database** (or use provided Docker setup)

### Local Development

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/gemini-screen-navigator.git
   cd gemini-screen-navigator
   ```

2. **Install Node dependencies:**
   ```bash
   pnpm install
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```

5. **Configure your `.env` file:**
   ```env
   # Google Cloud
   GCP_PROJECT_ID=your-project-id
   GEMINI_API_KEY=your-gemini-api-key
   GCS_BUCKET_NAME=your-bucket-name

   # Database
   DATABASE_URL=mysql://user:password@localhost:3306/gemini_navigator

   # OAuth (Manus)
   VITE_APP_ID=your-app-id
   JWT_SECRET=your-jwt-secret
   OAUTH_SERVER_URL=https://api.manus.im
   ```

6. **Set up the database:**
   ```bash
   pnpm db:push
   ```

7. **Start development server:**
   ```bash
   pnpm dev
   ```

   The application will be available at `http://localhost:3000`

---

## Usage

### Starting a Task

1. **Navigate to the dashboard** and authenticate
2. **Enter your task goal** (e.g., "Register a new account on example.com")
3. **Add optional context** for additional instructions
4. **Choose Demo Mode** if you want to simulate actions without actual execution
5. **Click START TASK** to begin

### Monitoring Execution

The dashboard displays:

- **Real-time progress** with step counter
- **Live execution logs** showing each action
- **Before/after screenshots** for verification
- **Pause/Resume controls** for manual intervention
- **Safety alerts** for dangerous operations requiring approval

### Viewing Results

After task completion, review:

- **Execution summary** with success rate
- **Screenshot gallery** showing all steps
- **Detailed logs** with timestamps
- **Generated report** in Markdown format
- **Evidence artifacts** stored in Google Cloud Storage

---

## API Reference

### tRPC Procedures

All procedures require authentication (except public endpoints).

#### `navigator.startTask`

Initiates a new automation task.

**Input:**
```typescript
{
  goal: string;           // Task objective
  context?: string;       // Additional instructions
  demoMode?: boolean;     // Simulate without actual execution
}
```

**Output:**
```typescript
{
  taskId: string;
  goal: string;
  status: "created";
  message: string;
}
```

#### `navigator.getTaskStatus`

Retrieves current task status and progress.

**Input:**
```typescript
{
  taskId: string;
}
```

**Output:**
```typescript
{
  taskId: string;
  status: "running" | "paused" | "completed" | "failed";
  progress: number;      // 0-100
  currentStep: number;
  totalSteps: number;
}
```

#### `navigator.getTaskReport`

Retrieves the final report for a completed task.

**Input:**
```typescript
{
  taskId: string;
}
```

**Output:**
```typescript
{
  taskId: string;
  success: boolean;
  duration: number;      // seconds
  totalSteps: number;
  successfulSteps: number;
  reportUrl: string;     // Markdown report URL
}
```

#### `navigator.approveAction`

Approves a pending action requiring user confirmation.

**Input:**
```typescript
{
  taskId: string;
  stepId: number;
}
```

---

## Deployment

### Docker Build

```bash
docker build -t gemini-screen-navigator:latest .
docker run -p 3000:3000 \
  -e GEMINI_API_KEY=your-key \
  -e GCP_PROJECT_ID=your-project \
  gemini-screen-navigator:latest
```

### Google Cloud Run

1. **Enable required APIs:**
   ```bash
   gcloud services enable run.googleapis.com cloudbuild.googleapis.com
   ```

2. **Deploy using Cloud Build:**
   ```bash
   gcloud builds submit --config=cloudbuild.yaml
   ```

3. **Or deploy directly:**
   ```bash
   gcloud run deploy gemini-screen-navigator \
     --source . \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your-key,GCP_PROJECT_ID=your-project \
     --memory 2Gi \
     --cpu 2 \
     --timeout 3600
   ```

4. **Access your deployment:**
   ```
   https://gemini-screen-navigator-[hash].run.app
   ```

---

## Safety & Security

### Safety Checks

The system automatically detects and flags:

- **Financial Operations**: Purchases, payments, transactions
- **Destructive Actions**: Deletions, data clearing, uninstalls
- **Communication**: Sending emails, messages, posts
- **Account Changes**: Password modifications, permission changes
- **System Changes**: Software installation, configuration updates

### Approval Workflow

For flagged operations:

1. Agent detects potentially dangerous action
2. Task pauses and requests user approval
3. User reviews action in dashboard
4. User approves or rejects
5. Agent continues or terminates accordingly

### Data Privacy

- Screenshots stored in encrypted Google Cloud Storage
- No data sent to third parties except Google APIs
- All processing happens server-side
- User data isolated per account

---

## Development

### Project Structure

```
gemini-screen-navigator/
├── client/                 # React frontend
│   ├── src/
│   │   ├── pages/         # Page components
│   │   ├── components/    # Reusable UI components
│   │   ├── lib/           # Utilities and hooks
│   │   └── App.tsx        # Main app component
│   └── public/            # Static assets
├── server/                # Express backend
│   ├── tools/             # Python automation tools
│   │   ├── screen_capture.py
│   │   ├── desktop_actions.py
│   │   ├── gemini_brain.py
│   │   ├── validator.py
│   │   ├── reporter.py
│   │   ├── safety_checker.py
│   │   └── gcs_storage.py
│   ├── agent/             # Agent orchestration
│   │   ├── state_machine.py
│   │   └── executor.py
│   ├── routers.ts         # tRPC procedure definitions
│   └── db.ts              # Database helpers
├── drizzle/               # Database schema
├── shared/                # Shared types and constants
├── Dockerfile             # Container definition
├── cloudbuild.yaml        # Google Cloud Build config
└── requirements.txt       # Python dependencies
```

### Running Tests

```bash
# Run vitest for backend tests
pnpm test

# Run with coverage
pnpm test:coverage
```

### Code Style

```bash
# Format code
pnpm format

# Type check
pnpm check
```

---

## Troubleshooting

### Common Issues

**Issue: "GEMINI_API_KEY not found"**

Solution: Ensure your `.env` file contains a valid Gemini API key from Google Cloud Console.

**Issue: "Database connection failed"**

Solution: Verify DATABASE_URL is correct and the database server is running.

**Issue: "Screenshots not saving"**

Solution: Check GCS_BUCKET_NAME and ensure the service account has Storage permissions.

**Issue: "Desktop actions not executing"**

Solution: Ensure the application has necessary permissions for mouse/keyboard control (may require running as administrator on Windows).

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## Support

For issues, questions, or suggestions:

- **GitHub Issues**: [Report a bug](https://github.com/yourusername/gemini-screen-navigator/issues)
- **Documentation**: [Full docs](https://github.com/yourusername/gemini-screen-navigator/wiki)
- **Email**: support@example.com

---

## Acknowledgments

- **Google Gemini API** for multimodal AI capabilities
- **Google Cloud Platform** for infrastructure
- **Open source community** for amazing tools and libraries

---

**Built for the Google Gemini Live Agent Challenge 2026**

*Last updated: February 21, 2026*
