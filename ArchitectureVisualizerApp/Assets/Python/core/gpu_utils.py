"""GPU detection and configuration utilities"""
import sys

def detect_gpu():
    """
    Detect available GPU and return configuration.
    
    Returns:
        dict: GPU information with keys:
            - available (bool): Whether GPU is available
            - device (str): Device type ('cuda', 'hip', or 'cpu')
            - name (str): GPU name if available
            - library (str): Library used for GPU support
    """
    gpu_info = {
        'available': False,
        'device': 'cpu',
        'name': None,
        'library': None
    }
    
    # Try CUDA (NVIDIA)
    try:
        import torch
        if torch.cuda.is_available():
            gpu_info['available'] = True
            gpu_info['device'] = 'cuda'
            gpu_info['name'] = torch.cuda.get_device_name(0)
            gpu_info['library'] = 'pytorch-cuda'
            return gpu_info
    except ImportError:
        pass
    except Exception:
        pass
    
    # Try ROCm (AMD)
    try:
        import torch
        if hasattr(torch, 'hip') and torch.hip.is_available():
            gpu_info['available'] = True
            gpu_info['device'] = 'hip'
            gpu_info['name'] = 'AMD GPU (ROCm)'
            gpu_info['library'] = 'pytorch-rocm'
            return gpu_info
    except (ImportError, AttributeError):
        pass
    except Exception:
        pass
    
    return gpu_info


def get_optimal_device():
    """
    Get the best available compute device.
    
    Returns:
        str: Device string ('cuda', 'hip', or 'cpu')
    """
    gpu = detect_gpu()
    return gpu['device']


def log_gpu_status():
    """Log GPU detection status to stderr for UI display"""
    gpu = detect_gpu()
    if gpu['available']:
        print(f"[GPU] Using {gpu['name']} ({gpu['library']})", file=sys.stderr)
    else:
        print(f"[GPU] No GPU detected, using CPU", file=sys.stderr)
    return gpu
