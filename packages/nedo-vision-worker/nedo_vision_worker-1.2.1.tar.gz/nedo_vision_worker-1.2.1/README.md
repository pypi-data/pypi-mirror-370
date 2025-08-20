# Nedo Vision Worker Service

A high-performance, multiplatform Python worker service for the Nedo Vision system that handles AI-powered computer vision tasks with GPU acceleration support.

## 🚀 Features

- **🎯 AI-Powered Computer Vision** - Advanced object detection and video processing
- **🔐 Token-Based Authentication** - Secure worker registration and management
- **⚡ GPU Acceleration** - NVIDIA CUDA support for high-performance inference
- **🌍 Multiplatform Support** - Linux, Windows, macOS, ARM devices, and cloud platforms
- **🚀 Jetson Optimized** - Native support for NVIDIA Jetson devices
- **☁️ Cloud Ready** - Docker, Kubernetes, and major cloud platform support
- **🔧 Self-Diagnostic** - Built-in system requirements checker
- **📊 Real-time Monitoring** - System usage and performance metrics

## 📋 System Requirements

### Minimum Requirements

- **Python**: 3.8+
- **CPU**: 2 cores, 1.5 GHz
- **RAM**: 2 GB
- **Storage**: 1 GB free space

### Recommended Requirements

- **CPU**: 4+ cores, 2.0+ GHz
- **RAM**: 4+ GB (8+ GB for GPU acceleration)
- **GPU**: NVIDIA GPU with CUDA support (optional)
- **Storage**: 5+ GB free space

### Supported Platforms

- **Linux** (x86_64, ARM64, ARMv7) - Ubuntu, Debian, CentOS, Alpine
- **Windows** (x86_64) - Windows 10+, Server 2019+
- **macOS** (x86_64, Apple Silicon) - macOS 10.15+
- **NVIDIA Jetson** - Nano, Xavier NX, Xavier AGX, Orin
- **Cloud Platforms** - AWS, GCP, Azure (with GPU instance support)

## 🛠️ Installation

### Quick Install (PyPI)

```bash
pip install nedo-vision-worker
```

### Platform-Specific Installation

#### Standard Linux/Windows/macOS

```bash
# Install from PyPI
pip install nedo-vision-worker

# Verify installation
nedo-worker doctor
```

#### NVIDIA Jetson Devices

```bash
# Use system OpenCV for optimal performance
sudo apt install python3-opencv

# Install without OpenCV dependency
pip install nedo-vision-worker --no-deps
pip install alembic ffmpeg-python grpcio pika protobuf psutil pynvml requests SQLAlchemy

# Verify Jetson-specific features
nedo-worker doctor
```

#### ARM Devices (Raspberry Pi, etc.)

```bash
# Install with ARM-optimized packages
pip install nedo-vision-worker

# For headless servers, use lightweight OpenCV
pip install opencv-python-headless --upgrade
```

#### Docker Deployment

```dockerfile
# GPU-enabled container
FROM nvidia/cuda:11.8-runtime-ubuntu20.04
RUN pip install nedo-vision-worker

# CPU-only container
FROM python:3.9-slim
RUN apt-get update && apt-get install -y ffmpeg
RUN pip install nedo-vision-worker
```

### Development Installation

```bash
# Clone the repository
git clone https://gitlab.com/sindika/research/nedo-vision/nedo-vision-worker-service
cd nedo-vision-worker-service

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install -e .[dev]
```

## 🔍 System Diagnostics

Before running the worker service, use the built-in diagnostic tool to verify your system:

```bash
nedo-worker doctor
```

This will check:

- ✅ Platform compatibility and architecture
- ✅ Python version and dependencies
- ✅ FFmpeg installation and functionality
- ✅ OpenCV installation and optimizations
- ✅ NVIDIA GPU support and capabilities
- ✅ Storage permissions

## 📖 Quick Start

### 1. Get Your Worker Token

1. Access the Nedo Vision frontend
2. Navigate to Worker Management
3. Create a new worker
4. Copy the generated authentication token

### 2. Run System Check

```bash
nedo-worker doctor
```

### 3. Start the Worker Service

```bash
# Basic usage
nedo-worker run --token YOUR_TOKEN_HERE

# With custom configuration
nedo-worker run --token YOUR_TOKEN_HERE \
                 --server-host custom.server.com \
                 --storage-path /custom/storage/path \
                 --system-usage-interval 60
```

## 💻

## 💻 Usage

### Command Line Interface

The service uses a modern CLI with subcommands:

```bash
# Check system compatibility and requirements
nedo-worker doctor

# Run the worker service
nedo-worker run --token YOUR_TOKEN

# Get help
nedo-worker --help
nedo-worker run --help
nedo-worker doctor --help
```

### Available Commands

#### `doctor` - System Diagnostics

```bash
# Run comprehensive system check
nedo-worker doctor

# Check specific components
nedo-worker doctor --verbose
```

#### `run` - Start Worker Service

```bash
# Basic usage
nedo-worker run --token YOUR_TOKEN

# Advanced configuration
nedo-worker run \
    --token YOUR_TOKEN \
    --server-host be.vision.sindika.co.id \
    --server-port 50051 \
    --storage-path ./data \
    --system-usage-interval 30
```

### Configuration Options

| Parameter                 | Description                       | Default                   | Required |
| ------------------------- | --------------------------------- | ------------------------- | -------- |
| `--token`                 | Worker authentication token       | -                         | ✅       |
| `--server-host`           | Backend server hostname           | `be.vision.sindika.co.id` | ❌       |
| `--server-port`           | Backend server port               | `50051`                   | ❌       |
| `--storage-path`          | Local storage directory ⚠️\*      | `./data`                  | ❌       |
| `--system-usage-interval` | System metrics interval (seconds) | `30`                      | ❌       |

> **⚠️ Storage Path Note**: If using **Nedo Vision Worker Core**, both services must use the **same storage path** for proper data sharing and model access.

### Programmatic Usage

```python
from nedo_vision_worker.worker_service import WorkerService

# Create service instance
service = WorkerService(
    server_host="be.vision.sindika.co.id",
    token="your-token-here",
    storage_path="./custom_storage",
    system_usage_interval=60
)

# Initialize and run
if service.initialize():
    print("Service initialized successfully")
    service.run()  # This blocks until service stops
else:
    print("Failed to initialize service")
```

### Connection Information Client

```python
from nedo_vision_worker.services.ConnectionInfoClient import ConnectionInfoClient

# Create client
client = ConnectionInfoClient(
    host="be.vision.sindika.co.id",
    port=50051,
    token="your-token-here"
)

# Get connection information
result = client.get_connection_info()
if result["success"]:
    print(f"RabbitMQ Host: {result['rabbitmq_host']}")
    print(f"RabbitMQ Port: {result['rabbitmq_port']}")
    print(f"Database URL: {result['database_url']}")
else:
    print(f"Error: {result['error']}")
```

## 🔐 Authentication Flow

1. **Worker Registration**: Create a worker through the Nedo Vision frontend
2. **Token Generation**: System generates a unique authentication token
3. **Service Initialization**: Worker service authenticates using the token
4. **Connection Setup**: Service establishes secure connections to backend services
5. **Task Processing**: Worker receives and processes computer vision tasks
6. **Monitoring**: Continuous system monitoring and health reporting

## ⚙️ Configuration Management

## ⚙️ Configuration Management

> **⚠️ Important Notice - Storage Path Coordination**
>
> If you're using **Nedo Vision Worker Core** alongside this service, ensure both services use the **same storage path**. This is critical for proper data sharing and model access between services.
>
> ```bash
> # Example: Both services should use identical storage paths
> nedo-worker run --token YOUR_TOKEN --storage-path /shared/nedo/storage
> nedo-worker-core --storage-path /shared/nedo/storage
> ```
>
> The storage path contains:
>
> - 📁 **Models** - Shared AI models and weights
> - 📁 **Temporary files** - Processing artifacts and cache
> - 📁 **Logs** - Service operation logs
> - 📁 **Configurations** - Runtime settings and preferences

### Environment Variables (Legacy Support)

```bash
export NEDO_WORKER_TOKEN="your-token-here"
export NEDO_SERVER_HOST="be.vision.sindika.co.id"
export NEDO_STORAGE_PATH="./data"

# Run with environment variables (deprecated)
nedo-worker run
```

### Configuration Priority

1. **Command-line arguments** (highest priority)
2. **Environment variables** (legacy support)
3. **Default values** (lowest priority)

## 🚀 Platform-Specific Setup

### Windows Setup

#### Prerequisites

```powershell
# Install Chocolatey (package manager)
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install FFmpeg
choco install ffmpeg -y

# Verify installation
ffmpeg -version
```

#### Worker Installation

```powershell
# Install Python package
pip install nedo-vision-worker

# Run system check
nedo-worker doctor

# Start worker
nedo-worker run --token YOUR_TOKEN
```

### Linux Setup

#### Ubuntu/Debian

```bash
# Update system
sudo apt update

# Install FFmpeg
sudo apt install ffmpeg python3-pip

# Install worker
pip3 install nedo-vision-worker

# Run diagnostics
nedo-worker doctor
```

#### CentOS/RHEL

```bash
# Install EPEL repository
sudo yum install epel-release

# Install dependencies
sudo yum install ffmpeg python3-pip

# Install worker
pip3 install nedo-vision-worker
```

### NVIDIA Jetson Setup

```bash
# Ensure JetPack is installed
sudo apt update

# Use system OpenCV (optimized for Jetson)
sudo apt install python3-opencv

# Install worker without OpenCV
pip3 install nedo-vision-worker --no-deps
pip3 install alembic ffmpeg-python grpcio pika protobuf psutil pynvml requests SQLAlchemy

# Verify GPU support
nedo-worker doctor

# Check Jetson stats
sudo /usr/bin/tegrastats
```

### macOS Setup

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install FFmpeg
brew install ffmpeg

# Install worker
pip3 install nedo-vision-worker

# Run diagnostics
nedo-worker doctor
```

## 🔧 Troubleshooting

### Common Issues

#### 1. FFmpeg Not Found

```bash
# Check if FFmpeg is installed
ffmpeg -version

# Install FFmpeg
# Ubuntu/Debian: sudo apt install ffmpeg
# Windows: choco install ffmpeg
# macOS: brew install ffmpeg
```

#### 2. OpenCV Issues on ARM

```bash
# For ARM devices, try headless version
pip uninstall opencv-python
pip install opencv-python-headless
```

#### 3. GPU Not Detected

```bash
# Check NVIDIA drivers
nvidia-smi

# Check CUDA installation
nvcc --version

# Run system diagnostics
nedo-worker doctor
```

#### 4. Connection Issues

```bash
# Test network connectivity
ping be.vision.sindika.co.id

# Check firewall settings
# Ensure port 50051 is accessible

# Verify token
nedo-worker run --token YOUR_TOKEN --verbose
```

### Debug Mode

```bash
# Run with verbose logging
nedo-worker run --token YOUR_TOKEN --verbose

# Check logs
tail -f ~/.nedo_worker/logs/worker.log
```

### Performance Optimization

#### For High-Performance Workloads

```bash
# Increase system usage interval
nedo-worker run --token YOUR_TOKEN --system-usage-interval 60

# Use dedicated storage path
nedo-worker run --token YOUR_TOKEN --storage-path /fast/ssd/storage
```

#### For Resource-Constrained Devices

```bash
# Use minimal configuration
nedo-worker run --token YOUR_TOKEN --system-usage-interval 120
```

### Development Setup

```bash
# Clone and setup
git clone https://gitlab.com/sindika/research/nedo-vision/nedo-vision-worker-service
cd nedo-vision-worker-service

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install in development mode
pip install -e .[dev]

# Run tests
pytest

# Format code
black .
isort .
```
