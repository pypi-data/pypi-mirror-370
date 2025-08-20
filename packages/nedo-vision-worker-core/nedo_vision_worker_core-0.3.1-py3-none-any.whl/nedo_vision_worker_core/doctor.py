#!/usr/bin/env python3
"""
Nedo Vision Worker Core Doctor

This module provides diagnostic capabilities to check system requirements
and dependencies for the Nedo Vision Worker Core.
"""

import subprocess
import sys
import platform
import shutil
import os
from pathlib import Path


def check_python_version():
    """Check if Python version meets requirements."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    min_version = (3, 8)
    
    if version >= min_version:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro} (meets requirement >= {min_version[0]}.{min_version[1]})")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (requires >= {min_version[0]}.{min_version[1]})")
        return False


def check_pytorch():
    """Check if PyTorch is properly installed."""
    print("🔥 Checking PyTorch...")
    
    try:
        import torch
        import torchvision
        
        torch_version = torch.__version__
        torchvision_version = torchvision.__version__
        
        print(f"   ✅ PyTorch {torch_version} installed")
        print(f"   ✅ TorchVision {torchvision_version} installed")
        
        # Check CUDA availability
        if torch.cuda.is_available():
            device_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            device_name = torch.cuda.get_device_name(current_device)
            
            print(f"   🚀 CUDA available with {device_count} device(s)")
            print(f"   🎮 Current device: {device_name}")
            
            # Check CUDA version
            cuda_version = torch.version.cuda
            if cuda_version:
                print(f"   🔧 CUDA version: {cuda_version}")
        else:
            print("   ⚠️ CUDA not available (using CPU only)")
        
        # Test basic tensor operations
        try:
            x = torch.randn(5, 3)
            y = torch.randn(3, 4)
            z = torch.mm(x, y)
            print("   ✅ PyTorch basic operations working")
            return True
        except Exception as e:
            print(f"   ❌ PyTorch basic operations failed: {e}")
            return False
            
    except ImportError as e:
        print(f"   ❌ PyTorch not installed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ PyTorch test failed: {e}")
        return False


def check_ultralytics():
    """Check if Ultralytics (YOLO) is properly installed."""
    print("🎯 Checking Ultralytics YOLO...")
    
    try:
        from ultralytics import YOLO
        import ultralytics
        
        version = ultralytics.__version__
        print(f"   ✅ Ultralytics {version} installed")
        
        # Test YOLO model loading (without downloading)
        try:
            # Check if we can import required modules
            from ultralytics.models import YOLO as YOLOModel
            from ultralytics.utils import checks
            print("   ✅ Ultralytics modules importing correctly")
            return True
        except Exception as e:
            print(f"   ⚠️ Ultralytics modules test failed: {e}")
            return False
            
    except ImportError:
        print("   ❌ Ultralytics not installed")
        return False
    except Exception as e:
        print(f"   ❌ Ultralytics test failed: {e}")
        return False


def check_opencv():
    """Check if OpenCV is properly installed."""
    print("👁️ Checking OpenCV...")
    
    try:
        import cv2
        version = cv2.__version__
        build_info = cv2.getBuildInformation()
        
        print(f"   ✅ OpenCV {version} installed")
        
        # Check OpenCV build configuration
        if "CUDA" in build_info:
            print("   🚀 OpenCV built with CUDA support")
        if "OpenMP" in build_info:
            print("   ⚡ OpenCV built with OpenMP support")
        
        # Check for platform-specific optimizations
        machine = platform.machine()
        if machine in ["aarch64", "armv7l", "arm64"]:
            if "NEON" in build_info:
                print("   🎯 OpenCV built with ARM NEON optimizations")
            else:
                print("   ⚠️ OpenCV may not have ARM optimizations")
        
        # Test basic functionality
        import numpy as np
        test_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test encoding/decoding
        _, encoded = cv2.imencode('.jpg', test_img)
        decoded = cv2.imdecode(encoded, cv2.IMREAD_COLOR)
        
        if decoded is not None:
            print("   ✅ OpenCV basic functionality working")
            return True
        else:
            print("   ❌ OpenCV encoding/decoding test failed")
            return False
            
    except ImportError:
        print("   ❌ OpenCV not installed")
        return False
    except Exception as e:
        print(f"   ❌ OpenCV test failed: {e}")
        return False


def check_ffmpeg():
    """Check if FFmpeg is installed and accessible."""
    print("🎬 Checking FFmpeg...")
    
    try:
        # Check if ffmpeg is in PATH
        ffmpeg_path = shutil.which("ffmpeg")
        if not ffmpeg_path:
            print("   ❌ FFmpeg not found in PATH")
            return False
        
        # Check ffmpeg version
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Extract version from output
            version_line = result.stdout.split('\n')[0]
            print(f"   ✅ {version_line}")
            print(f"   📍 Location: {ffmpeg_path}")
            return True
        else:
            print("   ❌ FFmpeg found but failed to get version")
            return False
            
    except subprocess.TimeoutExpired:
        print("   ❌ FFmpeg check timed out")
        return False
    except Exception as e:
        print(f"   ❌ Error checking FFmpeg: {e}")
        return False


def check_storage_access():
    """Check if storage directories are accessible."""
    print("💾 Checking storage access...")
    
    try:
        storage_path = Path("data")
        
        # Check if we can create the directory
        storage_path.mkdir(exist_ok=True)
        print(f"   ✅ Storage directory accessible: {storage_path.absolute()}")
        
        # Test write access
        test_file = storage_path / "test_access.txt"
        try:
            with open(test_file, 'w') as f:
                f.write("test")
            test_file.unlink()  # Clean up
            print("   ✅ Storage write access working")
            return True
        except Exception as e:
            print(f"   ❌ Storage write access failed: {e}")
            return False
            
    except Exception as e:
        print(f"   ❌ Storage access check failed: {e}")
        return False


def check_system_resources():
    """Check system resources (memory, disk space)."""
    print("🖥️ Checking system resources...")
    
    try:
        import psutil
        
        # Check memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        print(f"   💾 Total RAM: {memory_gb:.1f} GB")
        
        if memory_gb >= 4:
            print("   ✅ Sufficient RAM available")
        else:
            print("   ⚠️ Low RAM (recommended: 4+ GB)")
        
        # Check disk space
        disk = psutil.disk_usage('.')
        disk_free_gb = disk.free / (1024**3)
        print(f"   💿 Free disk space: {disk_free_gb:.1f} GB")
        
        if disk_free_gb >= 2:
            print("   ✅ Sufficient disk space available")
        else:
            print("   ⚠️ Low disk space (recommended: 2+ GB)")
        
        # Check CPU
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        print(f"   🔢 CPU cores: {cpu_count}")
        if cpu_freq:
            print(f"   ⚡ CPU frequency: {cpu_freq.current:.0f} MHz")
        
        return True
        
    except ImportError:
        print("   ❌ psutil not installed for system resource checks")
        return False
    except Exception as e:
        print(f"   ❌ System resource check failed: {e}")
        return False


def check_model_files():
    """Check if model files are available."""
    print("🤖 Checking model files...")
    
    try:
        # Check for YOLO model file
        model_file = Path("yolov11n.pt")
        if model_file.exists():
            size_mb = model_file.stat().st_size / (1024**2)
            print(f"   ✅ YOLO model found: {model_file} ({size_mb:.1f} MB)")
            return True
        else:
            print("   ⚠️ YOLO model file not found (will be downloaded on first use)")
            return True  # Not a critical failure
            
    except Exception as e:
        print(f"   ❌ Model file check failed: {e}")
        return False


def run_diagnostics():
    """Run all diagnostic checks."""
    print("🏥 Nedo Vision Worker Core - System Diagnostics")
    print("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("PyTorch", check_pytorch),
        ("Ultralytics YOLO", check_ultralytics),
        ("OpenCV", check_opencv),
        ("FFmpeg", check_ffmpeg),
        ("Storage Access", check_storage_access),
        ("System Resources", check_system_resources),
        ("Model Files", check_model_files),
    ]
    
    results = []
    
    for name, check_func in checks:
        print()
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ Unexpected error in {name}: {e}")
            results.append((name, False))
    
    # Summary
    print()
    print("=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:8} {name}")
        if result:
            passed += 1
    
    print()
    print(f"Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All checks passed! The system is ready for Nedo Vision Worker Core.")
        return True
    else:
        print("⚠️ Some checks failed. Please address the issues above.")
        return False


if __name__ == "__main__":
    run_diagnostics()
