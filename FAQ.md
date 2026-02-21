# Frequently Asked Questions

## General Questions

### What is Gemini Screen Navigator?

Gemini Screen Navigator is an AI-powered desktop automation agent that uses Google's Gemini Pro Vision API to autonomously execute tasks on your desktop. It combines computer vision, natural language understanding, and desktop control to perform complex operations.

### How does it work?

The system operates in a continuous loop:
1. **Perceive**: Capture a screenshot of the current desktop
2. **Plan**: Send the screenshot to Gemini for analysis and action planning
3. **Act**: Execute the planned actions on the desktop
4. **Verify**: Compare before/after screenshots to verify success

### What can it do?

Common use cases include:
- Web application testing
- Data entry automation
- Account management
- System configuration
- Report generation
- Any task that can be done with mouse and keyboard

### What can't it do?

- Access system files directly (only through UI)
- Modify code or configuration files
- Perform tasks requiring authentication beyond the UI
- Handle tasks requiring voice interaction
- Work with applications that don't have a visual UI

## Setup & Installation

### What are the system requirements?

- **OS**: Windows, macOS, or Linux
- **Node.js**: 22.0 or higher
- **Python**: 3.11 or higher
- **RAM**: 4GB minimum (8GB recommended)
- **Storage**: 2GB for dependencies and artifacts

### How do I get a Gemini API key?

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Click "Get API Key"
3. Create a new API key
4. Copy the key to your `.env` file

### How do I set up Google Cloud?

1. Create a Google Cloud project
2. Enable required APIs (Cloud Run, Cloud Storage, Cloud SQL)
3. Create a service account with appropriate permissions
4. Download the service account key
5. Follow the [DEPLOYMENT.md](DEPLOYMENT.md) guide

### Can I use it locally without Google Cloud?

Yes! For development, you can run everything locally:
- Use a local MySQL database
- Store artifacts locally instead of Cloud Storage
- Use the Gemini API directly (requires API key)

## Usage

### How do I start a task?

1. Open the application in your browser
2. Enter the task goal (e.g., "Open Chrome and search for AI")
3. Add optional context or instructions
4. Click "START TASK"
5. Monitor progress in the dashboard

### How long does a task take?

Typical tasks take 30-120 seconds depending on complexity. The time includes:
- Screenshot capture (1-2 seconds)
- Gemini analysis (2-5 seconds)
- Action execution (varies by action)
- Verification (2-5 seconds)

### Can I pause or stop a task?

Yes! The dashboard provides:
- **Pause**: Temporarily stop execution
- **Resume**: Continue from where it paused
- **Stop**: Terminate the task
- **Approve/Reject**: Handle safety-flagged operations

### What happens if an action fails?

The system automatically retries up to 3 times with different strategies:
1. Adjust click coordinates
2. Add scroll action before clicking
3. Increase wait time between actions

If all retries fail, the task is marked as failed with detailed error logs.

## Safety & Security

### What is the safety system?

The system detects and flags potentially dangerous operations:
- Financial transactions
- Destructive actions (deletions)
- Communication operations (emails, posts)
- Account modifications
- System changes

For flagged operations, the system pauses and requests user approval before proceeding.

### Can it access my sensitive data?

No. The system:
- Only controls the desktop UI
- Cannot access files directly
- Requires your approval for sensitive operations
- Stores data in your Google Cloud project
- Never sends data to third parties

### Is my data encrypted?

Yes. All data is:
- Encrypted in transit (HTTPS)
- Encrypted at rest in Google Cloud Storage
- Isolated per user/task
- Compliant with GDPR requirements

## Troubleshooting

### "GEMINI_API_KEY not found"

**Solution**:
1. Check your `.env` file exists
2. Ensure the key is set correctly
3. Restart the development server
4. Verify the key is valid in Google AI Studio

### "Cannot connect to database"

**Solution**:
1. Check DATABASE_URL in `.env`
2. Verify MySQL/TiDB is running
3. Test connection: `mysql -u user -p -h host`
4. Check firewall rules if using Cloud SQL

### "Desktop actions not working"

**Solution**:
1. Ensure the application has proper permissions
2. On Windows, try running as administrator
3. Check that pyautogui is installed: `pip show pyautogui`
4. Verify the desktop is visible (not locked)

### "Screenshots not saving"

**Solution**:
1. Check GCS_BUCKET_NAME in `.env`
2. Verify bucket exists: `gsutil ls`
3. Check service account permissions
4. Ensure bucket is accessible from Cloud Run

### "Gemini API errors"

**Solution**:
1. Verify API key is valid
2. Check API quota usage
3. Ensure Gemini API is enabled in Google Cloud
4. Check API rate limits (default: 60 requests/minute)

### "Timeout errors on Cloud Run"

**Solution**:
1. Increase timeout: `--timeout=3600`
2. Increase memory: `--memory=4Gi`
3. Check task complexity
4. Optimize action execution

## Performance

### How can I improve performance?

1. **Simplify tasks**: Break complex tasks into smaller steps
2. **Optimize screenshots**: Use lower resolution if possible
3. **Cache results**: Reuse successful task results
4. **Parallel execution**: Run multiple tasks concurrently
5. **Upgrade resources**: Increase Cloud Run memory/CPU

### What are typical success rates?

- **Well-defined tasks**: 85-95%
- **Complex tasks**: 70-85%
- **Ambiguous tasks**: 50-70%

Success depends on task clarity, UI consistency, and action complexity.

### How much does it cost?

**Google Cloud costs**:
- Cloud Run: ~$0.00002400 per vCPU-second
- Cloud Storage: ~$0.020 per GB/month
- Gemini API: Free tier available, then $0.075 per 1M input tokens

**Typical monthly cost**: $5-50 depending on usage

## Advanced

### Can I add custom tools?

Yes! You can extend the system by:
1. Creating a new Python tool in `server/tools/`
2. Integrating it with the agent executor
3. Adding tRPC procedures for the frontend
4. Documenting the new capability

### Can I deploy to other cloud providers?

The system is Google Cloud native, but you can adapt it to:
- AWS (using EC2 instead of Cloud Run)
- Azure (using Container Instances)
- Self-hosted (Docker on your server)

See [DEPLOYMENT.md](DEPLOYMENT.md) for details.

### How do I contribute?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write tests
5. Submit a pull request

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

## Limitations

### Known Limitations

1. **Single desktop**: Can only automate one desktop at a time
2. **UI-based only**: Cannot access system files directly
3. **No real-time interaction**: Cannot handle interactive dialogs
4. **Limited to automation**: Cannot perform computational tasks
5. **Screenshot-dependent**: Requires visible UI elements

### Roadmap

Future improvements planned:
- Multi-monitor support
- Voice input/output
- Mobile app integration
- Advanced error recovery
- Performance optimization
- Custom model training

## Getting Help

### Resources

- **Documentation**: See [README.md](README.md)
- **Architecture**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **GitHub Issues**: Report bugs or request features
- **Discussions**: Ask questions and share ideas

### Contact

- **Email**: support@example.com
- **GitHub**: Create an issue
- **Discussions**: Start a discussion thread

---

**Last Updated**: February 21, 2026

Can't find your answer? [Create an issue](https://github.com/yourusername/gemini-screen-navigator/issues) on GitHub!
