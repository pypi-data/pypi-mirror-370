# Use slim Python image as base
FROM python:3.11.11-slim

# Install git, gcloud, and other required packages, clean up in same layer to keep image small
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    git \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install gcloud SDK
RUN curl -sSL https://sdk.cloud.google.com | bash

# Update PATH to include gcloud
ENV PATH="/root/google-cloud-sdk/bin:$PATH"

# Set the working directory to /app
WORKDIR /app

# Set the GIT_KEY environment variable
ARG GIT_KEY
# Set DBT_USE_SSH environment variable to false
ARG DBT_USE_SSH=false
# Accept DBT_PROJECT as build argument
ARG DBT_PROJECT

# Copy requirements files
COPY requirements.txt .

# Install dbt and dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy shared configuration files
COPY profiles.yml .

# Copy the specific project directory
COPY projects/${DBT_PROJECT}/ .

# Create target directory
RUN mkdir -p /app/target

# Run dbt deps to have the dbt_packages folder
RUN dbt deps
