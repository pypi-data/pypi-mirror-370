# FROM registry.access.redhat.com/ubi8/python-312
FROM python:3.12.10-slim

# Set work directory
WORKDIR /opt/app-root

# Copy Python Project Files (Container context must be the `python` directory)
COPY . /opt/app-root

RUN mkdir -p /opt/app-root/.cache/uv

USER root

# Install system build dependencies and UV package manager
RUN apt-get update && apt-get install -y gcc g++ \
 && pip install uv

# Set environment variables for uv:
# UV_COMPILE_BYTECODE=1: Compiles Python files to .pyc for faster startup
# UV_LINK_MODE=copy: Ensures files are copied, not symlinked, which can avoid issues
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# Set environment variable so UV cache is placed in writable location
ENV UV_CACHE_DIR=/opt/app-root/.cache/uv

# Install dependencies using uv sync.
# --frozen: Ensures uv respects the uv.lock file
# --no-install-project: Prevents installing the project itself in this stage
# --no-dev: Excludes development dependencies
# --mount=type=cache: Leverages Docker's build cache for uv, speeding up repeated builds
RUN --mount=type=cache,target=/opt/app-root/.cache/uv \
    uv sync --frozen --no-install-project --no-dev

# Install the project
RUN --mount=type=cache,target=/opt/app-root/.cache/uv \
    uv sync --frozen --no-dev

# Allow non-root user to access the everything in app-root
RUN chgrp -R root /opt/app-root/ && chmod -R g+rwx /opt/app-root/

# Expose default port (change if needed)
# EXPOSE 10000
# Check the content of the image
RUN ls -al .
RUN ls -al .venv
RUN ls -al /opt/app-root/.cache/uv
# RUN tree /opt/app-root

RUN chown -R 1001:1001 /opt/app-root/
USER 1001
RUN id

# Run the agent
# CMD uv run app --host 0.0.0.0
CMD ["uv", "run", "axmp-container-openapi-mcp-server"]