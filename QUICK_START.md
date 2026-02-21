# Quick Start Guide

Get Gemini Screen Navigator running in 5 minutes.

## Prerequisites

- Node.js 22+
- Python 3.11+
- Google Gemini API Key
- Google Cloud Project ID

## Installation (5 minutes)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/gemini-screen-navigator.git
cd gemini-screen-navigator
```

### 2. Install Dependencies

```bash
# Install Node packages
pnpm install

# Install Python packages
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
# Required:
# - GEMINI_API_KEY=your-key-here
# - GCP_PROJECT_ID=your-project-id
```

### 4. Start Development Server

```bash
pnpm dev
```

Visit `http://localhost:3000` in your browser.

## First Task (2 minutes)

1. **Open the application** at `http://localhost:3000`
2. **Enter a task goal**: "Open Notepad and type 'Hello World'"
3. **Click START TASK**
4. **Watch the execution** in real-time
5. **View results** in the dashboard

## Deployment to Google Cloud (10 minutes)

```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Build and deploy
gcloud run deploy gemini-screen-navigator \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=$GEMINI_API_KEY,GCP_PROJECT_ID=$PROJECT_ID
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Check your `.env` file
- Ensure the key is valid
- Restart the development server

### "Cannot connect to database"
- Verify DATABASE_URL in `.env`
- Ensure database server is running
- Check MySQL/TiDB connection

### "Desktop actions not working"
- Ensure the application has proper permissions
- On Windows, may need to run as administrator
- Check that pyautogui is installed: `pip show pyautogui`

## Next Steps

- Read the full [README.md](README.md)
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- See [DEPLOYMENT.md](DEPLOYMENT.md) for production setup
- Review [CONTRIBUTING.md](CONTRIBUTING.md) to contribute

## Documentation

- **README.md** - Complete setup and usage guide
- **ARCHITECTURE.md** - System design and components
- **DEPLOYMENT.md** - Google Cloud deployment
- **PROJECT_DESCRIPTION.md** - Detailed project overview
- **DEMO_SCRIPT.md** - Video demonstration guide

## Support

- Check existing [GitHub Issues](https://github.com/yourusername/gemini-screen-navigator/issues)
- Read the [FAQ](FAQ.md)
- Create a new issue for bugs or feature requests

---

**Happy automating!** 🚀
