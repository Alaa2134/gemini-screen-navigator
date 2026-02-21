#!/usr/bin/env python3
"""
Google Cloud Run Deployment Script for Gemini Screen Navigator
This script handles the deployment of the project to Google Cloud Run
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📦 {description}")
    print(f"{'='*60}")
    print(f"$ {cmd}\n")
    
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        return False
    print(f"✅ {description} completed successfully")
    return True

def main():
    """Main deployment function"""
    
    # Get project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    print("\n" + "="*60)
    print("🚀 GEMINI SCREEN NAVIGATOR - GOOGLE CLOUD RUN DEPLOYMENT")
    print("="*60)
    
    # Step 1: Check if gcloud is installed
    print("\n📋 Checking prerequisites...")
    result = subprocess.run("which gcloud", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Google Cloud SDK not found. Please install it first.")
        print("   Visit: https://cloud.google.com/sdk/docs/install")
        return False
    print("✅ Google Cloud SDK found")
    
    # Step 2: Check if Docker is installed
    result = subprocess.run("which docker", shell=True, capture_output=True)
    if result.returncode != 0:
        print("❌ Docker not found. Please install it first.")
        print("   Visit: https://docs.docker.com/get-docker/")
        return False
    print("✅ Docker found")
    
    # Step 3: Get project ID from environment or user input
    project_id = os.getenv("GCP_PROJECT_ID")
    if not project_id:
        print("\n⚠️  GCP_PROJECT_ID not set in environment")
        print("   Please set it with: export GCP_PROJECT_ID=your-project-id")
        return False
    
    print(f"✅ Project ID: {project_id}")
    
    # Step 4: Set gcloud project
    if not run_command(
        f"gcloud config set project {project_id}",
        "Setting Google Cloud project"
    ):
        return False
    
    # Step 5: Enable required APIs
    apis = [
        "run.googleapis.com",
        "cloudbuild.googleapis.com",
        "storage-api.googleapis.com",
        "containerregistry.googleapis.com"
    ]
    
    print("\n📋 Enabling required Google Cloud APIs...")
    for api in apis:
        run_command(
            f"gcloud services enable {api}",
            f"Enabling {api}"
        )
    
    # Step 6: Create Cloud Storage bucket
    bucket_name = f"gemini-navigator-artifacts-{project_id}"
    print(f"\n📦 Creating Cloud Storage bucket: {bucket_name}")
    run_command(
        f"gsutil mb -p {project_id} gs://{bucket_name} 2>/dev/null || echo 'Bucket may already exist'",
        "Creating Cloud Storage bucket"
    )
    
    # Step 7: Build Docker image
    service_name = "gemini-screen-navigator"
    image_name = f"gcr.io/{project_id}/{service_name}"
    
    if not run_command(
        f"docker build -t {image_name}:latest .",
        "Building Docker image"
    ):
        return False
    
    # Step 8: Push image to Container Registry
    if not run_command(
        f"docker push {image_name}:latest",
        "Pushing image to Container Registry"
    ):
        return False
    
    # Step 9: Deploy to Cloud Run
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    if not gemini_api_key:
        print("⚠️  GEMINI_API_KEY not set in environment")
        print("   Please set it with: export GEMINI_API_KEY=your-api-key")
        return False
    
    deploy_cmd = f"""
    gcloud run deploy {service_name} \\
      --image={image_name}:latest \\
      --platform=managed \\
      --region=us-central1 \\
      --allow-unauthenticated \\
      --set-env-vars=GEMINI_API_KEY={gemini_api_key},GCP_PROJECT_ID={project_id},GCS_BUCKET_NAME={bucket_name} \\
      --memory=2Gi \\
      --cpu=2 \\
      --timeout=3600 \\
      --max-instances=100 \\
      --min-instances=0
    """
    
    if not run_command(deploy_cmd, "Deploying to Cloud Run"):
        return False
    
    # Step 10: Get service URL
    print("\n📋 Getting service URL...")
    result = subprocess.run(
        f"gcloud run services describe {service_name} --region=us-central1 --format='value(status.url)'",
        shell=True,
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        service_url = result.stdout.strip()
        print(f"\n✅ Deployment successful!")
        print(f"   Service URL: {service_url}")
        print(f"   GitHub: https://github.com/Alaa2134/gemini-screen-navigator")
        print(f"   Devpost: https://geminiliveagentchallenge.devpost.com/")
    else:
        print("⚠️  Could not retrieve service URL")
    
    print("\n" + "="*60)
    print("🎉 DEPLOYMENT COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Test the service URL in your browser")
    print("2. Record a demo video (see DEMO_SCRIPT.md)")
    print("3. Submit on Devpost (see SUBMISSION.md)")
    print("4. Share on social media with #GeminiLiveAgentChallenge")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
