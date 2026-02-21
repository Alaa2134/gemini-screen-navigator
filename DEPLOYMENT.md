# Deployment Guide - Google Cloud Run

This guide walks you through deploying Gemini Screen Navigator to Google Cloud Run.

## Prerequisites

- Google Cloud Project with billing enabled
- Google Cloud CLI (`gcloud`) installed and configured
- Docker installed locally (for testing)
- GitHub repository with project code

## Step 1: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  storage-api.googleapis.com \
  cloudsql.googleapis.com \
  artifactregistry.googleapis.com
```

## Step 2: Create Cloud Storage Bucket

```bash
# Set your project ID
export PROJECT_ID=$(gcloud config get-value project)

# Create bucket for artifacts
gsutil mb -p $PROJECT_ID gs://gemini-navigator-artifacts-$PROJECT_ID

# Set bucket permissions
gsutil iam ch serviceAccount:cloud-run@$PROJECT_ID.iam.gserviceaccount.com:objectAdmin \
  gs://gemini-navigator-artifacts-$PROJECT_ID
```

## Step 3: Set Environment Variables

```bash
export PROJECT_ID=$(gcloud config get-value project)
export REGION=us-central1
export SERVICE_NAME=gemini-screen-navigator
export IMAGE_NAME=gcr.io/$PROJECT_ID/$SERVICE_NAME
```

## Step 4: Build and Push Docker Image

### Option A: Using Cloud Build (Recommended)

```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_GEMINI_API_KEY=$GEMINI_API_KEY
```

### Option B: Build Locally and Push

```bash
# Build image
docker build -t $IMAGE_NAME:latest .

# Configure Docker authentication
gcloud auth configure-docker

# Push to Container Registry
docker push $IMAGE_NAME:latest
```

## Step 5: Deploy to Cloud Run

```bash
gcloud run deploy $SERVICE_NAME \
  --image=$IMAGE_NAME:latest \
  --platform=managed \
  --region=$REGION \
  --allow-unauthenticated \
  --set-env-vars=\
GEMINI_API_KEY=$GEMINI_API_KEY,\
GCP_PROJECT_ID=$PROJECT_ID,\
GCS_BUCKET_NAME=gemini-navigator-artifacts-$PROJECT_ID,\
DATABASE_URL=$DATABASE_URL \
  --memory=2Gi \
  --cpu=2 \
  --timeout=3600 \
  --max-instances=100 \
  --min-instances=0
```

## Step 6: Verify Deployment

```bash
# Get service URL
gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)'

# Test the service
curl https://$SERVICE_NAME-[hash].run.app/health
```

## Step 7: Set Up Cloud SQL (Optional)

If using Cloud SQL instead of local MySQL:

```bash
# Create Cloud SQL instance
gcloud sql instances create gemini-navigator-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=$REGION

# Create database
gcloud sql databases create gemini_navigator \
  --instance=gemini-navigator-db

# Create user
gcloud sql users create gemini-user \
  --instance=gemini-navigator-db \
  --password=[SECURE_PASSWORD]

# Get connection string
gcloud sql instances describe gemini-navigator-db \
  --format='value(connectionName)'
```

## Step 8: Configure Continuous Deployment

### GitHub Actions (Recommended)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          project_id: ${{ secrets.GCP_PROJECT_ID }}
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          export_default_credentials: true
      
      - name: Build and push to Container Registry
        run: |
          gcloud builds submit \
            --config=cloudbuild.yaml \
            --substitutions=_GEMINI_API_KEY=${{ secrets.GEMINI_API_KEY }}
      
      - name: Deploy to Cloud Run
        run: |
          gcloud run deploy gemini-screen-navigator \
            --image=gcr.io/${{ secrets.GCP_PROJECT_ID }}/gemini-screen-navigator:latest \
            --platform=managed \
            --region=us-central1 \
            --allow-unauthenticated
```

## Step 9: Monitor Deployment

```bash
# View logs
gcloud run services describe $SERVICE_NAME --region=$REGION

# Stream logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=$SERVICE_NAME" \
  --limit=50 \
  --format=json

# View metrics
gcloud monitoring dashboards create --config-from-file=dashboard.json
```

## Troubleshooting

### Issue: "Permission denied" errors

**Solution**: Ensure service account has required permissions:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:cloud-run@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/storage.admin

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member=serviceAccount:cloud-run@$PROJECT_ID.iam.gserviceaccount.com \
  --role=roles/cloudsql.client
```

### Issue: "Container failed to start"

**Solution**: Check logs for errors:

```bash
gcloud run services describe $SERVICE_NAME --region=$REGION
gcloud logging read "resource.type=cloud_run_revision" --limit=100 --format=json
```

### Issue: "Timeout" errors

**Solution**: Increase timeout and memory:

```bash
gcloud run services update $SERVICE_NAME \
  --region=$REGION \
  --timeout=3600 \
  --memory=4Gi
```

## Rollback

To rollback to a previous version:

```bash
# List revisions
gcloud run revisions list --service=$SERVICE_NAME --region=$REGION

# Route traffic to previous revision
gcloud run services update-traffic $SERVICE_NAME \
  --region=$REGION \
  --to-revisions=[REVISION_ID]=100
```

## Cost Optimization

- **Min instances**: Set to 0 for development (pay only when used)
- **Memory**: Start with 2GB, increase only if needed
- **CPU**: 2 vCPU is sufficient for most tasks
- **Scaling**: Set max instances based on expected load

## Security Best Practices

1. **Never commit secrets**: Use Cloud Secret Manager
   ```bash
   echo -n "$GEMINI_API_KEY" | gcloud secrets create gemini-api-key --data-file=-
   ```

2. **Use service accounts**: Don't use default compute service account

3. **Enable VPC**: Restrict access to internal services

4. **Enable audit logging**: Track all API calls

5. **Use Cloud Armor**: Protect against DDoS attacks

## Next Steps

1. Set up monitoring and alerting
2. Configure custom domain
3. Set up CI/CD pipeline
4. Enable Cloud CDN for static assets
5. Configure backup and disaster recovery

---

**Last Updated**: February 21, 2026
