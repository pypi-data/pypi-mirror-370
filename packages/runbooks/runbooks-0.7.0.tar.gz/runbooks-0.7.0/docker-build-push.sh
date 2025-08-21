#!/bin/bash

## ==========================================================
## Script: docker-build-push.sh
## Description: Build and Push multi-arch Docker images using Docker BuildX
## Maintainer: Nhat-Thanh Nguyen <nnthanh101@gmail.com>
## Version: 1.0.1
## cd .devcontainer && ./docker-build-push.sh python tech-docs
## ./docker-build-push.sh nginx latest     ## docker push nnthanh101/nginx:latest
## ./docker-build-push.sh devops latest    ## docker push nnthanh101/devops:latest
## ./docker-build-push.sh cloudops latest  ## docker push nnthanh101/cloudops:latest
## ./docker-build-push.sh analytics latest ## docker push nnthanh101/analytics:latest
## ==========================================================

VENV_NAME=${1:-"runbooks"}  ## Allow optional argument for custom image name
DOCKER_REPO="nnthanh101"
# DOCKER_PATH=$VENV_NAME      ## Allow optional argument for custom Dockerfile folder
DOCKER_PATH=.               ## ./Dockerfile

IMAGE_NAME="$DOCKER_REPO/$VENV_NAME"
TAG=${2:-"latest"}          ## Default tag is 'latest' if not provided
FULL_IMAGE_NAME="$IMAGE_NAME:$TAG"

echo "Building Docker Image: $FULL_IMAGE_NAME"
# echo "cd 1xOps/DevOps/.devcontainer && ls"

## 1.1. Validate Docker BuildX
if ! docker buildx version > /dev/null 2>&1; then
    echo "Error: Docker BuildX is not installed or configured. Exiting."
    exit 1
fi

## 1.2. Create or reuse BuildX Builder
BUILDER_NAME="devops-builder-$VENV_NAME"
if ! docker buildx inspect $BUILDER_NAME > /dev/null 2>&1; then
    echo "[INFO] Creating BuildX Builder: $BUILDER_NAME"
    docker buildx create --name $BUILDER_NAME --use --driver docker-container
else
    echo "[INFO] Reusing existing BuildX Builder: $BUILDER_NAME"
    docker buildx use $BUILDER_NAME
fi

## 1.3. Clean up unused resources from previous builds
docker buildx prune --all --force

## 2. Build and Push Multi-Arch Images
echo "Building and Pushing Docker Image..."
docker buildx build \
--tag $FULL_IMAGE_NAME \
--build-arg IMAGE_TAG=$TAG \
--platform linux/arm64,linux/amd64 \
--builder $BUILDER_NAME \
--push $DOCKER_PATH || { \
    echo "Error: Docker buildx build failed."; \
    exit 1; \
}

echo "Docker Image Successfully Built and Pushed: $FULL_IMAGE_NAME"

## 3. Cleanup unused BuildX resources
echo "[INFO] Cleaning up BuildX Builder: $BUILDER_NAME"
docker buildx rm $BUILDER_NAME || echo "[WARNING] Failed to clean up builder. Please check manually."

exit 0
