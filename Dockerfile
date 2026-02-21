# Multi-stage build for Gemini Screen Navigator

# Stage 1: Build frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app

# Copy package files
COPY package.json pnpm-lock.yaml ./

# Install dependencies
RUN npm install -g pnpm && pnpm install --frozen-lockfile

# Copy source
COPY client ./client
COPY server ./server
COPY shared ./shared
COPY drizzle ./drizzle
COPY tsconfig.json vite.config.ts tailwind.config.ts postcss.config.js ./

# Build frontend
RUN pnpm build

# Stage 2: Build backend
FROM python:3.11-slim AS backend-builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libssl-dev \
    libffi-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Stage 3: Runtime
FROM node:22-alpine
WORKDIR /app

# Install Python runtime
RUN apk add --no-cache python3 py3-pip

# Install system dependencies for desktop automation
RUN apk add --no-cache \
    xvfb \
    x11-server \
    xdotool \
    scrot \
    libx11 \
    libxext \
    libxrender

# Copy built frontend from stage 1
COPY --from=frontend-builder /app/dist ./dist

# Copy server code
COPY server ./server
COPY shared ./shared
COPY drizzle ./drizzle
COPY package.json pnpm-lock.yaml ./

# Copy Python dependencies from stage 2
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

# Copy Python tools
COPY server/tools ./server/tools
COPY server/agent ./server/agent

# Install Node dependencies for production
RUN npm install -g pnpm && pnpm install --frozen-lockfile --prod

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', (r) => {if (r.statusCode !== 200) throw new Error(r.statusCode)})"

# Start application
CMD ["npm", "start"]
