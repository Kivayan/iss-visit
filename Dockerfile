FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy requirements
COPY pyproject.toml uv.lock ./

# Install uv for faster dependency management
RUN pip install uv

# Install dependencies
RUN uv sync --frozen

# Copy application code
COPY main.py .

# Create data directory for SQLite database
RUN mkdir -p /data

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uv", "run", "python", "main.py"]
