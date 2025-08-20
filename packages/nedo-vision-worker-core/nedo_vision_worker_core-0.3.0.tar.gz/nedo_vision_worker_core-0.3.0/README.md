# Nedo Vision Worker Core

A powerful Python library for AI-powered computer vision processing in the Nedo Vision platform. This library provides real-time video processing, object detection, PPE compliance monitoring, and safety violation detection with an extensible callback system.

## Features

- **Real-time AI Detection**: Advanced PPE and safety compliance detection
- **Multi-stream Processing**: Handle multiple video sources simultaneously
- **Extensible Callbacks**: Event-driven architecture for detection handling
- **System Diagnostics**: Built-in health checking and troubleshooting
- **Database Integration**: Persistent storage for detections and configurations
- **Drawing Utilities**: Rich visualization tools for detections
- **GPU Acceleration**: CUDA support for optimal performance
- **RTMP Streaming**: Real-time video streaming capabilities

## Installation

### Basic Installation

Install the package from PyPI:

```bash
pip install nedo-vision-worker-core
```

### Installation with RF-DETR Support

RF-DETR is an optional dependency for advanced object detection. Install it separately:

```bash
# Install the main package
pip install nedo-vision-worker-core
```

### GPU Support

For GPU support with CUDA 12.1:

```bash
pip install nedo-vision-worker-core --extra-index-url https://download.pytorch.org/whl/cu121
```

### Development Installation

For development with all tools:

```bash
pip install nedo-vision-worker-core[dev]
```

## Quick Start

### Using the CLI

After installation, you can use the worker core CLI:

```bash
# Show CLI help
nedo-worker-core --help

# Run with default settings
nedo-worker-core run

# Run with custom configuration
nedo-worker-core run --log-level DEBUG --storage-path /data

# System health check
nedo-worker-core doctor

# Run with custom server configuration
nedo-worker-core run --storage-path /custom/storage --rtmp-server rtmp://server.com:1935/live
```

### Configuration Options

The service supports various configuration options:

- `--drawing-assets`: Path to drawing assets directory
- `--log-level`: Logging level (DEBUG|INFO|WARNING|ERROR)
- `--storage-path`: Storage path for databases and files
- `--rtmp-server`: RTMP server URL for video streaming

### Detection Callbacks

The worker core provides a unified callback system for handling detection events:

```python
from nedo_vision_worker_core import (
    CoreService,
    DetectionType,
    CallbackTrigger,
    DetectionData,
    register_immediate_ppe_callback
)

def handle_ppe_detection(detection_data: DetectionData):
    """Handle PPE detection events."""
    if detection_data.has_violations():
        # Send alert for safety violations
        send_safety_alert(
            person_id=detection_data.person_id,
            violations=[v.label for v in detection_data.get_violations()],
            confidence=detection_data.confidence_score,
            image_path=detection_data.image_path
        )

    # Log all detections for compliance tracking
    log_detection_event(detection_data)

def handle_area_violation(detection_data: DetectionData):
    """Handle restricted area violations."""
    # Immediate security response
    trigger_security_alert(
        location=detection_data.pipeline_id,
        person_id=detection_data.person_id,
        timestamp=detection_data.timestamp
    )

# Quick registration
register_immediate_ppe_callback("safety_monitor", handle_ppe_detection)

# Advanced registration
CoreService.register_callback(
    name="security_monitor",
    callback=handle_area_violation,
    trigger=CallbackTrigger.ON_NEW_DETECTION,
    detection_types=[DetectionType.AREA_VIOLATION]
)

# Start processing
service = CoreService()
service.run()
```

### Advanced Usage

For interval-based monitoring and complex workflows:

```python
from nedo_vision_worker_core import (
    register_interval_ppe_callback,
    register_immediate_area_callback,
    IntervalMetadata
)

def handle_ongoing_ppe_violations(detection_data: DetectionData):
    """Handle PPE violations that are currently active (called periodically while violations persist)."""
    metadata = detection_data.get_interval_metadata()
    if metadata:
        # This callback is only triggered when there are active violations
        current_violations = metadata['current_violation_state']
        people_in_violation = metadata['unique_persons_in_violation']

        # Take action for ongoing violations
        if people_in_violation > 0:
            # Escalate persistent violations
            escalate_safety_violation(
                pipeline_id=detection_data.pipeline_id,
                violation_types=current_violations,
                affected_count=people_in_violation,
                state_time=metadata['state_timestamp']
            )

            # Continue monitoring until violations are resolved
            log_ongoing_violation_state(detection_data, metadata)

def emergency_response(detection_data: DetectionData):
    """Handle immediate area violations."""
    # Trigger immediate emergency protocols
    emergency_alert = {
        'alert_type': 'RESTRICTED_AREA_BREACH',
        'location': detection_data.pipeline_id,
        'person_id': detection_data.person_id,
        'confidence': detection_data.confidence_score,
        'timestamp': detection_data.timestamp,
        'evidence_image': detection_data.image_path
    }

    # Send to security team
    notify_security_team(emergency_alert)

    # Log incident for investigation
    log_security_incident(emergency_alert)

def handle_ongoing_area_violations(detection_data: DetectionData):
    """Handle area violations that are currently active (called periodically while violations persist)."""
    metadata = detection_data.get_interval_metadata()
    if metadata:
        # This is called every X seconds while people are still in restricted areas
        active_violations = metadata['total_active_violations']

        if active_violations > 0:
            # Continuous monitoring for ongoing security breaches
            maintain_security_alert(
                location=detection_data.pipeline_id,
                ongoing_violations=active_violations,
                duration_check=metadata['state_timestamp']
            )

# Register immediate callbacks (triggered on each new detection)
register_immediate_area_callback("immediate_security", emergency_response)

# Register interval callbacks (triggered periodically ONLY when violations are currently active)
register_interval_ppe_callback("ongoing_ppe_monitor", handle_ongoing_ppe_violations, interval_seconds=30)
register_interval_area_callback("ongoing_area_monitor", handle_ongoing_area_violations, interval_seconds=15)

# Monitor multiple detection types with custom logic
def safety_coordinator(detection_data: DetectionData):
    """Coordinate safety responses across all detection types."""
    if detection_data.detection_type == DetectionType.PPE_DETECTION:
        handle_ppe_safety(detection_data)
    elif detection_data.detection_type == DetectionType.AREA_VIOLATION:
        handle_security_breach(detection_data)

CoreService.register_callback(
    name="safety_coordinator",
    callback=safety_coordinator,
    trigger=CallbackTrigger.ON_NEW_DETECTION,
    detection_types=[DetectionType.PPE_DETECTION, DetectionType.AREA_VIOLATION]
)
```

### Programmatic Usage

You can use the core service programmatically in your applications:

```python
from nedo_vision_worker_core import CoreService

# Basic usage - start the service with default settings
service = CoreService()
service.run()

# Custom configuration
service = CoreService(
    log_level="INFO",
    storage_path="./data"
)
service.run()

# With error handling
try:
    service = CoreService(log_level="DEBUG")
    service.run()
except KeyboardInterrupt:
    print("Service stopped")
except Exception as e:
    print(f"Error: {e}")
```

## Architecture

### Core Components

- **CoreService**: Main service orchestrator with callback management
- **Detection Pipeline**: AI model processing with PyTorch backend
- **Callback System**: Unified event handling with immediate and interval triggers
- **Resource Monitor**: System resource monitoring (GPU, CPU, memory)
- **Database Manager**: Persistent storage for detections and configurations

### Callback System

#### Trigger Types

- **`ON_NEW_DETECTION`**: Triggered immediately on each detection
- **`ON_VIOLATION_INTERVAL`**: Triggered periodically only when violations occur in the interval

#### Detection Types

- **`PPE_DETECTION`**: Personal Protective Equipment compliance
- **`AREA_VIOLATION`**: Restricted area violations
- **`GENERAL_DETECTION`**: All detection events

#### Data Structure

```python
class DetectionData:
    detection_id: str
    person_id: str
    pipeline_id: str
    detection_type: DetectionType
    confidence_score: float
    timestamp: datetime
    image_path: str
    metadata: dict

    def get_violations(self) -> List[DetectionAttribute]
    def get_compliance(self) -> List[DetectionAttribute]
    def has_violations(self) -> bool
    def get_interval_metadata(self) -> Optional[IntervalMetadata]

class IntervalMetadata(TypedDict):
    state_timestamp: str              # ISO format datetime of current state
    total_active_violations: int      # Current number of active violations
    unique_persons_in_violation: int  # Number of people currently in violation
    current_violation_state: Dict[str, int]  # Current violation types and counts
    violation_summary: Dict[str, int] # violation_type -> count (deprecated, use current_violation_state)
    total_violations: int            # total violations in interval (deprecated, use total_active_violations)
    violation_count_in_interval: int # violations in this specific interval
    interval_start: str              # ISO format datetime
    interval_end: str                # ISO format datetime
    unique_persons: int              # total unique persons in interval
```

#### API Methods

```python
# Core callback registration methods
CoreService.register_callback(name, callback, trigger, detection_types, interval_seconds)
CoreService.unregister_callback(name)
CoreService.list_callbacks()

# Convenience functions for common use cases
register_immediate_ppe_callback(name, callback)
register_immediate_area_callback(name, callback)
register_interval_ppe_callback(name, callback, interval_seconds)
register_interval_area_callback(name, callback, interval_seconds)

# Example: Managing callbacks programmatically
def setup_safety_monitoring():
    """Setup comprehensive safety monitoring system."""

    # Register immediate response callbacks
    register_immediate_ppe_callback("ppe_safety", handle_ppe_violations)
    register_immediate_area_callback("area_security", handle_area_breaches)

    # Register periodic reporting
    register_interval_ppe_callback("hourly_report", generate_hourly_report, interval_seconds=3600)

    # Verify registration
    active_callbacks = CoreService.list_callbacks()
    logging.info(f"Active monitoring: {len(active_callbacks)} callbacks registered")

    return active_callbacks

# Cleanup callbacks when needed
def cleanup_monitoring():
    """Remove specific callbacks."""
    CoreService.unregister_callback("ppe_safety")
    CoreService.unregister_callback("area_security")
```

### Dependencies

The service relies on several key technologies:

- **PyTorch**: Deep learning framework with CUDA support
- **OpenCV**: Computer vision and video processing
- **SQLAlchemy**: Database ORM and management
- **FFmpeg**: Video streaming and processing
- **Ultralytics**: YOLO model implementations

## Development Setup

For development and testing:

```bash
# Clone and setup development environment
git clone <repository-url>
cd nedo-vision-worker-core-v2

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate     # Windows

# Install in development mode
pip install -e .

# Run tests
python test.py

# Check system health
nedo-worker-core doctor
```

## Troubleshooting

### Common Issues

1. **CUDA not detected**: Ensure NVIDIA drivers and CUDA toolkit are installed
2. **FFmpeg not found**: Install FFmpeg for video processing capabilities
3. **Permission errors**: Check storage directory permissions
4. **Model loading issues**: Verify model files and network connectivity

### Support

For issues and questions:

- Check the logs for detailed error information
- Run `nedo-worker-core doctor` for system diagnostics
- Verify all dependencies are properly installed
