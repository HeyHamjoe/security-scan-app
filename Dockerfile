FROM python:3.10-slim

# Install dependencies: Java, curl, jq, and unzip
RUN apt-get update && apt-get install -y \
    openjdk-17-jre-headless \
    curl \
    jq \
    unzip

# Dynamically fetch and download the latest ZAP version with verified URL
RUN DOWNLOAD_URL=$(curl -s https://api.github.com/repos/zaproxy/zaproxy/releases/latest | jq -r '.assets[] | select(.name | test("ZAP_.*\\.zip")) | .browser_download_url') && \
    curl -L $DOWNLOAD_URL -o zap.zip && \
    if ! unzip zap.zip -d /opt/zap; then \
        echo "Failed to download or unzip ZAP. Check URL or connection." && exit 1; \
    fi && \
    rm zap.zip

# Set ZAP home
ENV ZAP_PATH=/opt/zap

# Set working directory
WORKDIR /app

# Copy application files (including templates)
COPY . /app

# Create the reports directory
RUN mkdir -p /app/reports

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports for Flask and OWASP ZAP
EXPOSE 5000 8080

# Copy and set the startup script
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Run the startup script
CMD ["/start.sh"]