import { describe, expect, it } from "vitest";

describe("Secrets Validation", () => {
  it("should have required environment variables set", () => {
    // Check if Gemini API key is available
    const geminiKey = process.env.GEMINI_API_KEY;
    expect(geminiKey).toBeDefined();
    expect(geminiKey).not.toBe("");
    
    // Check if GCP Project ID is available
    const gcpProjectId = process.env.GCP_PROJECT_ID;
    expect(gcpProjectId).toBeDefined();
    expect(gcpProjectId).not.toBe("");
    
    // Check if AWS credentials are available
    const awsAccessKey = process.env.AWS_ACCESS_KEY_ID;
    const awsSecretKey = process.env.AWS_SECRET_ACCESS_KEY;
    const awsBucket = process.env.AWS_S3_BUCKET;
    
    expect(awsAccessKey).toBeDefined();
    expect(awsSecretKey).toBeDefined();
    expect(awsBucket).toBeDefined();
  });

  it("should validate Gemini API key format", () => {
    const geminiKey = process.env.GEMINI_API_KEY;
    // Gemini API keys typically have a specific format
    expect(geminiKey).toMatch(/^[A-Za-z0-9_-]+$/);
  });

  it("should validate GCP Project ID format", () => {
    const gcpProjectId = process.env.GCP_PROJECT_ID;
    // GCP Project IDs are lowercase with hyphens
    expect(gcpProjectId).toMatch(/^[a-z0-9-]+$/);
  });

  it("should validate AWS S3 bucket name format", () => {
    const bucket = process.env.AWS_S3_BUCKET;
    // S3 bucket names follow specific rules
    expect(bucket).toMatch(/^[a-z0-9.-]+$/);
    expect(bucket?.length).toBeGreaterThanOrEqual(3);
    expect(bucket?.length).toBeLessThanOrEqual(63);
  });
});
