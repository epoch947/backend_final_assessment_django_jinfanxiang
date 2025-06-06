# Dockerfile

# 1. Base image: slim Python 3.11 (you can pin a different version if desired)
FROM python:3.11-slim

# 2. Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set working directory
WORKDIR /app

# 4. Install system dependencies needed to build psycopg2 and any C-based packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       build-essential \
       libpq-dev \
       gcc \
       postgresql-client \
       # (Optional) if yuse Pillow: libjpeg-dev libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy requirements and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 6. Copy the entire project into the container
COPY . /app/

# 7. Copy entrypoint script and ensure it’s executable
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# 8. Expose port 8000 for Django
EXPOSE 8000

# 9. Set the default entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]
