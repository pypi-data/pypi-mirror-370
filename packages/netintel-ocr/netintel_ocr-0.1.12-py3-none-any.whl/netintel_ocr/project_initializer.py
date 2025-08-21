"""
Project Initializer for NetIntel-OCR v0.1.11
Creates complete containerized environment with Docker, Helm, and configuration files.
"""

import os
import shutil
from pathlib import Path
from typing import Optional
import yaml
import json


class ProjectInitializer:
    """Initialize NetIntel-OCR project with Docker and Kubernetes support."""
    
    def __init__(self, base_dir: str = "./netintel-ocr"):
        """
        Initialize the project initializer.
        
        Args:
            base_dir: Base directory for project initialization
        """
        self.base_dir = Path(base_dir)
        self.ollama_host = os.getenv("OLLAMA_HOST", "http://192.168.68.20:11434")
    
    def initialize_project(self, force: bool = False) -> bool:
        """
        Initialize complete NetIntel-OCR project structure.
        
        Args:
            force: Force overwrite existing files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if directory exists
            if self.base_dir.exists() and not force:
                print(f"❌ Directory {self.base_dir} already exists. Use --force to overwrite.")
                return False
            
            # Create directory structure
            self._create_directory_structure()
            
            # Create Docker files
            self._create_dockerfile()
            self._create_docker_compose()
            
            # Create Helm charts
            self._create_helm_chart()
            
            # Create configuration files
            self._create_config_yaml()
            self._create_env_file()
            
            # Create README
            self._create_readme()
            
            print(f"✅ Successfully initialized NetIntel-OCR project at {self.base_dir}")
            print(f"\n📋 Next steps:")
            print(f"   1. cd {self.base_dir}")
            print(f"   2. Update .env with your Ollama server address")
            print(f"   3. docker-compose up -d")
            print(f"   4. Place PDFs in ./input directory")
            print(f"   5. docker-compose run --rm netintel-ocr /data/input/document.pdf")
            
            return True
            
        except Exception as e:
            print(f"❌ Error initializing project: {e}")
            return False
    
    def _create_directory_structure(self):
        """Create the project directory structure."""
        directories = [
            self.base_dir / "docker",
            self.base_dir / "helm" / "templates",
            self.base_dir / "config",
            self.base_dir / "input",
            self.base_dir / "output",
            self.base_dir / "scripts",
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _create_dockerfile(self):
        """Create Dockerfile for NetIntel-OCR."""
        # First create requirements.txt
        requirements_content = '''# NetIntel-OCR Requirements
pillow>=11.2.1
pymupdf>=1.26.1
requests>=2.32.4
tqdm>=4.67.1
opencv-python-headless>=4.5.0
pdfplumber>=0.10.0
pandas>=2.0.0
jsonschema>=4.0.0
pyyaml>=6.0.0
netintel-ocr
'''
        requirements_path = self.base_dir / "docker" / "requirements.txt"
        requirements_path.write_text(requirements_content)
        
        dockerfile_content = '''FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    libmupdf-dev \\
    mupdf-tools \\
    libglib2.0-0 \\
    libsm6 \\
    libxext6 \\
    libxrender-dev \\
    libgomp1 \\
    wget \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p /data/input /data/output /data/models /config

# Set environment variables
ENV OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
ENV NETINTEL_OUTPUT=/data/output
ENV NETINTEL_CONFIG=/config/config.yml
ENV PYTHONUNBUFFERED=1

# Create non-root user
RUN useradd -m -u 1000 netintel && \\
    chown -R netintel:netintel /data /config

USER netintel

WORKDIR /data

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \\
    CMD curl -f ${OLLAMA_HOST}/api/tags || exit 1

ENTRYPOINT ["netintel-ocr"]
CMD ["--help"]
'''
        
        dockerfile_path = self.base_dir / "docker" / "Dockerfile"
        dockerfile_path.write_text(dockerfile_content)
    
    def _create_docker_compose(self):
        """Create docker-compose.yml with MinIO integration."""
        compose_content = '''version: '3.8'

services:
  netintel-ocr:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    container_name: netintel-ocr
    volumes:
      - ../input:/data/input
      - ../output:/data/output
      - ../config:/config
    environment:
      - OLLAMA_HOST=${OLLAMA_HOST:-http://192.168.68.20:11434}
      - MINIO_ENDPOINT=http://minio:9000
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
      - NETINTEL_LOG_LEVEL=${NETINTEL_LOG_LEVEL:-INFO}
    depends_on:
      minio:
        condition: service_healthy
    networks:
      - netintel-network
    restart: unless-stopped

  minio:
    image: minio/minio:latest
    container_name: netintel-minio
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - ../output:/data
      - minio-data:/minio-data
    environment:
      - MINIO_ROOT_USER=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_ROOT_PASSWORD=${MINIO_SECRET_KEY:-minioadmin}
      - MINIO_VOLUMES=/minio-data
    command: server /minio-data --console-address ":9001"
    networks:
      - netintel-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:9000/minio/health/live"]
      interval: 30s
      timeout: 20s
      retries: 3
    restart: unless-stopped

  minio-init:
    image: minio/mc:latest
    container_name: netintel-minio-init
    depends_on:
      minio:
        condition: service_healthy
    environment:
      - MINIO_ACCESS_KEY=${MINIO_ACCESS_KEY:-minioadmin}
      - MINIO_SECRET_KEY=${MINIO_SECRET_KEY:-minioadmin}
    entrypoint: >
      /bin/sh -c "
      mc alias set myminio http://minio:9000 $${MINIO_ACCESS_KEY} $${MINIO_SECRET_KEY};
      mc mb myminio/lancedb || true;
      mc mb myminio/documents || true;
      mc policy set public myminio/lancedb;
      mc policy set public myminio/documents;
      mc version enable myminio/lancedb || true;
      echo 'MinIO initialization complete';
      exit 0;
      "
    networks:
      - netintel-network

volumes:
  minio-data:
    driver: local

networks:
  netintel-network:
    driver: bridge
'''
        
        compose_path = self.base_dir / "docker" / "docker-compose.yml"
        compose_path.write_text(compose_content)
    
    def _create_helm_chart(self):
        """Create Helm chart for Kubernetes deployment."""
        # Chart.yaml
        chart_yaml = '''apiVersion: v2
name: netintel-ocr
description: A Helm chart for NetIntel-OCR with MinIO integration
type: application
version: 0.1.11
appVersion: "0.1.11"
keywords:
  - pdf-processing
  - ocr
  - vector-database
  - lancedb
  - minio
maintainers:
  - name: NetIntel-OCR Team
    email: support@netintel-ocr.io
'''
        
        # values.yaml
        values_yaml = '''# Default values for netintel-ocr

replicaCount: 1

image:
  repository: netintel-ocr
  pullPolicy: IfNotPresent
  tag: "0.1.11"

nameOverride: ""
fullnameOverride: ""

serviceAccount:
  create: true
  annotations: {}
  name: ""

# External Ollama configuration
ollama:
  host: "http://ollama-service.ollama-namespace.svc.cluster.local:11434"
  timeout: 30

# MinIO configuration
minio:
  enabled: true
  mode: standalone
  replicas: 1
  rootUser: minioadmin
  rootPassword: minioadmin
  persistence:
    enabled: true
    size: 100Gi
    storageClass: "standard"
  
  buckets:
    - name: lancedb
      policy: public
      versioning: true
    - name: documents
      policy: public

# Storage configuration
storage:
  input:
    enabled: true
    size: 50Gi
    storageClass: "standard"
    accessMode: ReadWriteMany
  
  output:
    enabled: true
    size: 100Gi
    storageClass: "standard"
    accessMode: ReadWriteMany

# ConfigMap settings
config:
  processing:
    maxPages: 100
    mode: hybrid
    timeouts:
      textExtraction: 120
      networkDetection: 60
  
  models:
    text: "nanonets-ocr-s:latest"
    network: "qwen2.5vl:latest"
    embedding: "qwen3-embedding:4b"
  
  vector:
    enabled: true
    chunkSize: 1000
    chunkOverlap: 100

# Resources
resources:
  limits:
    cpu: 4
    memory: 8Gi
  requests:
    cpu: 2
    memory: 4Gi

# Autoscaling
autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
  targetMemoryUtilizationPercentage: 80

# Ingress
ingress:
  enabled: true
  className: "nginx"
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size: "100m"
  hosts:
    - host: netintel-ocr.local
      paths:
        - path: /
          pathType: Prefix
  tls: []

nodeSelector: {}
tolerations: []
affinity: {}
'''
        
        # deployment.yaml template
        deployment_yaml = '''apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "netintel-ocr.fullname" . }}
  labels:
    {{- include "netintel-ocr.labels" . | nindent 4 }}
spec:
  {{- if not .Values.autoscaling.enabled }}
  replicas: {{ .Values.replicaCount }}
  {{- end }}
  selector:
    matchLabels:
      {{- include "netintel-ocr.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      annotations:
        checksum/config: {{ include (print $.Template.BasePath "/configmap.yaml") . | sha256sum }}
      labels:
        {{- include "netintel-ocr.selectorLabels" . | nindent 8 }}
    spec:
      serviceAccountName: {{ include "netintel-ocr.serviceAccountName" . }}
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
          imagePullPolicy: {{ .Values.image.pullPolicy }}
          env:
            - name: OLLAMA_HOST
              value: {{ .Values.ollama.host }}
            - name: MINIO_ENDPOINT
              value: "http://{{ include "netintel-ocr.fullname" . }}-minio:9000"
            - name: MINIO_ACCESS_KEY
              value: {{ .Values.minio.rootUser }}
            - name: MINIO_SECRET_KEY
              value: {{ .Values.minio.rootPassword }}
          volumeMounts:
            - name: config
              mountPath: /config
            - name: input
              mountPath: /data/input
            - name: output
              mountPath: /data/output
          resources:
            {{- toYaml .Values.resources | nindent 12 }}
      volumes:
        - name: config
          configMap:
            name: {{ include "netintel-ocr.fullname" . }}
        - name: input
          persistentVolumeClaim:
            claimName: {{ include "netintel-ocr.fullname" . }}-input
        - name: output
          persistentVolumeClaim:
            claimName: {{ include "netintel-ocr.fullname" . }}-output
'''
        
        # _helpers.tpl
        helpers_tpl = '''{{/*
Expand the name of the chart.
*/}}
{{- define "netintel-ocr.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "netintel-ocr.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "netintel-ocr.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "netintel-ocr.labels" -}}
helm.sh/chart: {{ include "netintel-ocr.chart" . }}
{{ include "netintel-ocr.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "netintel-ocr.selectorLabels" -}}
app.kubernetes.io/name: {{ include "netintel-ocr.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "netintel-ocr.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "netintel-ocr.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}
'''
        
        # Write Helm files
        (self.base_dir / "helm" / "Chart.yaml").write_text(chart_yaml)
        (self.base_dir / "helm" / "values.yaml").write_text(values_yaml)
        (self.base_dir / "helm" / "templates" / "deployment.yaml").write_text(deployment_yaml)
        (self.base_dir / "helm" / "templates" / "_helpers.tpl").write_text(helpers_tpl)
    
    def _create_config_yaml(self):
        """Create default configuration YAML file."""
        config = {
            "processing": {
                "max_pages": 100,
                "mode": "hybrid",
                "timeouts": {
                    "text_extraction": 120,
                    "network_detection": 60,
                    "component_extraction": 60,
                    "mermaid_generation": 60
                },
                "confidence": {
                    "network_detection": 0.7,
                    "table_detection": 0.6
                }
            },
            "models": {
                "text": {
                    "primary": "nanonets-ocr-s:latest",
                    "fallback": "qwen2.5vl:latest"
                },
                "network": {
                    "primary": "qwen2.5vl:latest",
                    "fallback": "llava:latest"
                },
                "embedding": {
                    "model": "qwen3-embedding:4b",
                    "dimension": 2560
                }
            },
            "vector": {
                "enabled": True,
                "chunk_size": 1000,
                "chunk_overlap": 100,
                "chunk_strategy": "semantic",
                "lancedb": {
                    "local_path": "/data/output/lancedb",
                    "centralized": False,
                    "batch_size": 100
                }
            },
            "storage": {
                "input_dir": "/data/input",
                "output_dir": "/data/output",
                "s3": {
                    "enabled": True,
                    "endpoint": "http://minio:9000",
                    "bucket": "lancedb",
                    "region": "us-east-1"
                },
                "cleanup": {
                    "keep_images": False,
                    "archive_after_days": 30,
                    "compress_archives": True
                }
            },
            "ollama": {
                "host": "${OLLAMA_HOST:-http://192.168.68.20:11434}",
                "timeout": 30,
                "keep_alive": "5m",
                "expected_models": [
                    "nanonets-ocr-s:latest",
                    "qwen2.5vl:latest",
                    "qwen3-embedding:4b"
                ]
            },
            "logging": {
                "level": "INFO",
                "file": "/data/output/netintel-ocr.log",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
            "performance": {
                "max_workers": 4,
                "max_memory_mb": 4096,
                "cache": {
                    "enabled": True,
                    "path": "/data/output/.cache",
                    "max_size_mb": 1024
                }
            },
            "network_diagram": {
                "use_icons": True,
                "fast_extraction": False,
                "multi_diagram": False,
                "diagram_only": False
            },
            "table_extraction": {
                "enabled": True,
                "method": "hybrid",
                "skip_toc": True
            }
        }
        
        config_path = self.base_dir / "config" / "config.yml"
        with open(config_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
    
    def _create_env_file(self):
        """Create .env file with environment variables."""
        env_content = f'''# NetIntel-OCR Environment Variables
# Generated by netintel-ocr --init

# Ollama Configuration (External Server)
OLLAMA_HOST={self.ollama_host}

# MinIO Configuration
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_BUCKET=lancedb

# NetIntel-OCR Settings
NETINTEL_OUTPUT=/data/output
NETINTEL_CONFIG=/config/config.yml
NETINTEL_LOG_LEVEL=INFO

# Resource Limits
DOCKER_MEMORY_LIMIT=8g
DOCKER_CPU_LIMIT=4

# Vector Database Configuration
NETINTEL_LANCEDB_URI=s3://minio:9000/lancedb
NETINTEL_CENTRALIZED_DB=false
NETINTEL_EMBEDDING_MODEL=qwen3-embedding:4b

# Query Defaults
NETINTEL_QUERY_LIMIT=10
NETINTEL_SIMILARITY_THRESHOLD=0.7
'''
        
        env_path = self.base_dir / ".env"
        env_path.write_text(env_content)
    
    def _create_readme(self):
        """Create README with instructions."""
        readme_content = '''# NetIntel-OCR Containerized Environment

This directory contains a complete NetIntel-OCR deployment with Docker and Kubernetes support.

## Quick Start

### Using Docker Compose

1. **Update Ollama Server Address**:
   Edit `.env` and set your Ollama server address:
   ```
   OLLAMA_HOST=http://your-ollama-server:11434
   ```

2. **Start Services**:
   ```bash
   cd docker
   docker-compose up -d
   ```

3. **Process Documents**:
   Place PDFs in the `input/` directory, then run:
   ```bash
   docker-compose run --rm netintel-ocr /data/input/document.pdf
   ```

4. **Access MinIO Console**:
   - URL: http://localhost:9001
   - Username: minioadmin
   - Password: minioadmin

### Using Kubernetes

1. **Install Helm Chart**:
   ```bash
   helm install netintel-ocr ./helm \\
     --namespace netintel-ocr \\
     --create-namespace \\
     --set ollama.host=http://your-ollama-server:11434
   ```

2. **Check Deployment**:
   ```bash
   kubectl get all -n netintel-ocr
   ```

## Directory Structure

```
.
├── docker/               # Docker files
│   ├── Dockerfile
│   └── docker-compose.yml
├── helm/                 # Kubernetes Helm chart
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
├── config/               # Configuration files
│   └── config.yml
├── input/                # Input PDFs
├── output/               # Processing output
│   └── <md5>/           # Per-document folders
│       ├── markdown/
│       ├── lancedb/
│       └── tables/
└── .env                  # Environment variables
```

## Configuration

### config.yml
Main configuration file for processing settings, models, and storage options.

### .env
Environment variables for Docker deployment.

### helm/values.yaml
Kubernetes deployment configuration.

## Features

- **Vector Generation**: Automatic LanceDB vector files
- **MinIO Integration**: S3-compatible storage
- **External Ollama**: Uses existing Ollama server
- **Per-Document Processing**: Isolated MD5-based folders
- **Kubernetes Ready**: Full Helm chart included

## Next Steps

- Process multiple documents: `docker-compose run --rm netintel-ocr /data/input/*.pdf`
- Query vectors (coming in v0.1.12): `netintel-ocr --query "network topology"`
- Scale with Kubernetes: Edit `helm/values.yaml` and redeploy

## Support

For issues or questions, please visit:
https://github.com/netintel-ocr/netintel-ocr
'''
        
        readme_path = self.base_dir / "README.md"
        readme_path.write_text(readme_content)