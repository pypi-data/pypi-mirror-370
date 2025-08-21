"""
Device Manager - Hardware-Agnostic Device Detection and Management

This module provides automatic detection and management of the best available
computational device (CUDA, MPS, CPU) for PyTorch operations. It implements
a prioritized device detection system that seamlessly works across different
hardware configurations.

Key Features:
- Automatic detection of NVIDIA CUDA devices
- Apple Metal Performance Shaders (MPS) support for Apple Silicon
- Graceful fallback to CPU when no GPU is available
- Global device management with thread-safety
- Comprehensive logging and diagnostics
- Memory management utilities
- Device capability detection

Classes:
    DeviceManager: Singleton class for device management
    DeviceCapabilities: Data class for device capabilities
    DeviceMemoryManager: Memory management utilities

Functions:
    get_device(): Get the globally configured device
    get_device_info(): Get detailed device information
    set_device(): Manually set device (for testing)

Author: Multi-Objective Optimization Laboratory
Version: 3.6.6 GPU Accelerated
"""

import logging
import threading
import psutil
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

import torch
import numpy as np

logger = logging.getLogger(__name__)


class DeviceType(Enum):
    """Enumeration of supported device types."""
    CUDA = "cuda"
    MPS = "mps"  
    CPU = "cpu"


@dataclass
class DeviceCapabilities:
    """Data class holding device capabilities and specifications."""
    device_type: DeviceType
    device_name: str
    total_memory: int  # in bytes
    available_memory: int  # in bytes
    compute_capability: Optional[Tuple[int, int]] = None  # (major, minor) for CUDA
    cores: Optional[int] = None
    max_threads_per_block: Optional[int] = None
    supports_fp16: bool = False
    supports_bfloat16: bool = False


class DeviceManager:
    """
    Singleton class for managing computational devices across the application.
    
    This class implements a prioritized device detection system:
    1. NVIDIA CUDA (highest priority)
    2. Apple MPS (second priority) 
    3. CPU (fallback)
    
    The device is selected once at initialization and used throughout the
    application lifecycle for consistent performance.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern implementation with thread safety."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DeviceManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the device manager (only once due to singleton pattern)."""
        if self._initialized:
            return
            
        self._device = None
        self._device_type = None
        self._capabilities = None
        self._memory_fraction = 0.8  # Use 80% of GPU memory by default
        
        # Perform device detection and initialization
        self._detect_and_initialize_device()
        self._initialized = True
        
        logger.info(f"DeviceManager initialized with device: {self._device}")
    
    def _detect_and_initialize_device(self) -> None:
        """
        Detect and initialize the best available computational device.
        
        Priority order:
        1. NVIDIA CUDA - Check for CUDA availability and functionality
        2. Apple MPS - Check for MPS availability on Apple Silicon
        3. CPU - Always available as fallback
        """
        logger.info("Starting device detection...")
        
        # Priority 1: NVIDIA CUDA
        if self._try_cuda():
            return
            
        # Priority 2: Apple MPS (Metal Performance Shaders)
        if self._try_mps():
            return
            
        # Priority 3: CPU (always available)
        self._initialize_cpu()
        
    def _try_cuda(self) -> bool:
        """
        Attempt to initialize CUDA device.
        
        Returns:
            bool: True if CUDA was successfully initialized, False otherwise
        """
        try:
            if not torch.cuda.is_available():
                logger.info("CUDA not available on this system")
                return False
                
            # Check if CUDA is functional (not just available)
            try:
                # Create a small test tensor to verify CUDA functionality
                test_tensor = torch.randn(10, 10, device='cuda')
                test_result = torch.matmul(test_tensor, test_tensor)
                del test_tensor, test_result
                torch.cuda.empty_cache()
                
            except Exception as e:
                logger.warning(f"CUDA available but not functional: {e}")
                return False
            
            # Get CUDA device information
            device_count = torch.cuda.device_count()
            current_device = torch.cuda.current_device()
            device_name = torch.cuda.get_device_name(current_device)
            
            # Get memory information
            total_memory = torch.cuda.get_device_properties(current_device).total_memory
            reserved_memory = torch.cuda.memory_reserved(current_device)
            available_memory = total_memory - reserved_memory
            
            # Get compute capability
            major, minor = torch.cuda.get_device_capability(current_device)
            
            self._device = torch.device(f'cuda:{current_device}')
            self._device_type = DeviceType.CUDA
            self._capabilities = DeviceCapabilities(
                device_type=DeviceType.CUDA,
                device_name=device_name,
                total_memory=total_memory,
                available_memory=available_memory,
                compute_capability=(major, minor),
                supports_fp16=major >= 7,  # Tensor cores available from compute 7.0+
                supports_bfloat16=major >= 8  # BFloat16 from compute 8.0+
            )
            
            # Set memory management
            if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                torch.cuda.set_per_process_memory_fraction(self._memory_fraction, current_device)
            
            logger.info(f"CUDA initialized successfully:")
            logger.info(f"  Device: {device_name} (Device {current_device})")
            logger.info(f"  Compute Capability: {major}.{minor}")
            logger.info(f"  Total Memory: {total_memory / 1e9:.1f} GB")
            logger.info(f"  Available Memory: {available_memory / 1e9:.1f} GB")
            logger.info(f"  FP16 Support: {self._capabilities.supports_fp16}")
            logger.info(f"  BFloat16 Support: {self._capabilities.supports_bfloat16}")
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to initialize CUDA: {e}")
            return False
    
    def _try_mps(self) -> bool:
        """
        Attempt to initialize Apple MPS device.
        
        Returns:
            bool: True if MPS was successfully initialized, False otherwise
        """
        try:
            if not hasattr(torch.backends, 'mps') or not torch.backends.mps.is_available():
                logger.info("MPS not available on this system")
                return False
                
            # Check if MPS is functional
            try:
                # Create a small test tensor to verify MPS functionality
                test_tensor = torch.randn(10, 10, device='mps')
                test_result = torch.matmul(test_tensor, test_tensor)
                del test_tensor, test_result
                
            except Exception as e:
                logger.warning(f"MPS available but not functional: {e}")
                return False
            
            self._device = torch.device('mps')
            self._device_type = DeviceType.MPS
            
            # Get basic system information for MPS
            # Note: MPS doesn't provide as detailed memory info as CUDA
            try:
                # Get system memory as proxy for MPS memory
                system_memory = psutil.virtual_memory()
                total_memory = system_memory.total
                available_memory = system_memory.available
                
                self._capabilities = DeviceCapabilities(
                    device_type=DeviceType.MPS,
                    device_name="Apple MPS",
                    total_memory=total_memory,
                    available_memory=available_memory,
                    supports_fp16=True,  # MPS supports FP16
                    supports_bfloat16=False  # MPS typically doesn't support BFloat16
                )
                
                logger.info(f"MPS initialized successfully:")
                logger.info(f"  Device: Apple Metal Performance Shaders")
                logger.info(f"  System Memory: {total_memory / 1e9:.1f} GB")
                logger.info(f"  Available Memory: {available_memory / 1e9:.1f} GB")
                logger.info(f"  FP16 Support: {self._capabilities.supports_fp16}")
                
            except Exception as e:
                logger.warning(f"Could not get MPS memory info: {e}")
                self._capabilities = DeviceCapabilities(
                    device_type=DeviceType.MPS,
                    device_name="Apple MPS",
                    total_memory=0,
                    available_memory=0,
                    supports_fp16=True
                )
            
            return True
            
        except Exception as e:
            logger.warning(f"Failed to initialize MPS: {e}")
            return False
    
    def _initialize_cpu(self) -> None:
        """Initialize CPU device (always succeeds)."""
        self._device = torch.device('cpu')
        self._device_type = DeviceType.CPU
        
        # Get CPU information
        try:
            cpu_count = psutil.cpu_count(logical=True)
            system_memory = psutil.virtual_memory()
            
            self._capabilities = DeviceCapabilities(
                device_type=DeviceType.CPU,
                device_name=f"CPU ({cpu_count} cores)",
                total_memory=system_memory.total,
                available_memory=system_memory.available,
                cores=cpu_count,
                supports_fp16=False,  # CPU typically uses FP32
                supports_bfloat16=False
            )
            
            logger.info(f"CPU initialized as fallback device:")
            logger.info(f"  CPU Cores: {cpu_count}")
            logger.info(f"  System Memory: {system_memory.total / 1e9:.1f} GB")
            logger.info(f"  Available Memory: {system_memory.available / 1e9:.1f} GB")
            
        except Exception as e:
            logger.warning(f"Could not get CPU info: {e}")
            self._capabilities = DeviceCapabilities(
                device_type=DeviceType.CPU,
                device_name="CPU",
                total_memory=0,
                available_memory=0
            )
    
    @property
    def device(self) -> torch.device:
        """Get the current computational device."""
        return self._device
    
    @property
    def device_type(self) -> DeviceType:
        """Get the current device type."""
        return self._device_type
    
    @property
    def capabilities(self) -> DeviceCapabilities:
        """Get the device capabilities."""
        return self._capabilities
    
    def get_device_info(self) -> Dict[str, Any]:
        """
        Get comprehensive device information.
        
        Returns:
            Dict containing device specifications and capabilities
        """
        info = {
            "device": str(self._device),
            "device_type": self._device_type.value,
            "device_name": self._capabilities.device_name,
            "total_memory_gb": self._capabilities.total_memory / 1e9,
            "available_memory_gb": self._capabilities.available_memory / 1e9,
            "supports_fp16": self._capabilities.supports_fp16,
            "supports_bfloat16": self._capabilities.supports_bfloat16,
        }
        
        if self._capabilities.compute_capability:
            info["compute_capability"] = f"{self._capabilities.compute_capability[0]}.{self._capabilities.compute_capability[1]}"
        
        if self._capabilities.cores:
            info["cores"] = self._capabilities.cores
            
        return info
    
    def to_device(self, tensor: torch.Tensor) -> torch.Tensor:
        """
        Move a tensor to the managed device.
        
        Args:
            tensor: Input tensor
            
        Returns:
            Tensor moved to the managed device
        """
        return tensor.to(self._device)
    
    def empty_cache(self) -> None:
        """Empty the device cache if applicable."""
        if self._device_type == DeviceType.CUDA:
            torch.cuda.empty_cache()
        # MPS and CPU don't have explicit cache clearing
    
    def get_memory_usage(self) -> Dict[str, float]:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary with memory usage in GB
        """
        if self._device_type == DeviceType.CUDA:
            return {
                "allocated_gb": torch.cuda.memory_allocated() / 1e9,
                "reserved_gb": torch.cuda.memory_reserved() / 1e9,
                "max_allocated_gb": torch.cuda.max_memory_allocated() / 1e9,
                "max_reserved_gb": torch.cuda.max_memory_reserved() / 1e9,
            }
        else:
            # For CPU/MPS, use system memory
            memory = psutil.virtual_memory()
            return {
                "total_system_gb": memory.total / 1e9,
                "available_system_gb": memory.available / 1e9,
                "used_system_gb": memory.used / 1e9,
                "percent_used": memory.percent,
            }
    
    def set_memory_fraction(self, fraction: float) -> None:
        """
        Set the fraction of GPU memory to use.
        
        Args:
            fraction: Fraction between 0.0 and 1.0
        """
        if not 0.0 < fraction <= 1.0:
            raise ValueError("Memory fraction must be between 0.0 and 1.0")
            
        self._memory_fraction = fraction
        
        if self._device_type == DeviceType.CUDA:
            current_device = torch.cuda.current_device()
            if hasattr(torch.cuda, 'set_per_process_memory_fraction'):
                torch.cuda.set_per_process_memory_fraction(fraction, current_device)
            logger.info(f"Set CUDA memory fraction to {fraction}")


class DeviceMemoryManager:
    """Utility class for device memory management."""
    
    def __init__(self, device_manager: DeviceManager):
        self.device_manager = device_manager
    
    def optimize_for_batch_size(self, tensor_size: Tuple[int, ...], dtype: torch.dtype = torch.float32) -> int:
        """
        Estimate optimal batch size based on available memory.
        
        Args:
            tensor_size: Size of a single tensor (excluding batch dimension)
            dtype: Data type of tensors
            
        Returns:
            Recommended batch size
        """
        try:
            # Calculate memory per sample in bytes
            element_size = torch.tensor([], dtype=dtype).element_size()
            elements_per_sample = np.prod(tensor_size)
            bytes_per_sample = elements_per_sample * element_size
            
            # Get available memory
            if self.device_manager.device_type == DeviceType.CUDA:
                available_memory = torch.cuda.get_device_properties(0).total_memory * 0.8  # Use 80%
                used_memory = torch.cuda.memory_allocated()
                free_memory = available_memory - used_memory
            else:
                # For CPU/MPS, use system memory
                memory = psutil.virtual_memory()
                free_memory = memory.available * 0.5  # Use 50% of available system memory
            
            # Calculate batch size (leave some margin)
            safety_factor = 0.8
            max_batch_size = int((free_memory * safety_factor) / bytes_per_sample)
            
            # Ensure minimum batch size of 1
            return max(1, max_batch_size)
            
        except Exception as e:
            logger.warning(f"Could not estimate batch size: {e}")
            return 32  # Default fallback
    
    def check_memory_available(self, required_bytes: int) -> bool:
        """
        Check if sufficient memory is available.
        
        Args:
            required_bytes: Required memory in bytes
            
        Returns:
            True if sufficient memory is available
        """
        try:
            if self.device_manager.device_type == DeviceType.CUDA:
                available_memory = torch.cuda.get_device_properties(0).total_memory * 0.8
                used_memory = torch.cuda.memory_allocated()
                free_memory = available_memory - used_memory
            else:
                memory = psutil.virtual_memory()
                free_memory = memory.available * 0.5
            
            return free_memory >= required_bytes
            
        except Exception as e:
            logger.warning(f"Could not check memory availability: {e}")
            return True  # Assume available if check fails


# Global device manager instance
_device_manager = None
_device_lock = threading.Lock()


def get_device_manager() -> DeviceManager:
    """
    Get the global device manager instance.
    
    Returns:
        DeviceManager singleton instance
    """
    global _device_manager
    if _device_manager is None:
        with _device_lock:
            if _device_manager is None:
                _device_manager = DeviceManager()
    return _device_manager


def get_device() -> torch.device:
    """
    Get the global computational device.
    
    Returns:
        torch.device: The optimal device for computations
    """
    return get_device_manager().device


def get_device_info() -> Dict[str, Any]:
    """
    Get comprehensive device information.
    
    Returns:
        Dictionary containing device specifications
    """
    return get_device_manager().get_device_info()


def to_device(tensor: torch.Tensor) -> torch.Tensor:
    """
    Move a tensor to the optimal device.
    
    Args:
        tensor: Input tensor
        
    Returns:
        Tensor moved to the optimal device
    """
    return get_device_manager().to_device(tensor)


def empty_cache() -> None:
    """Empty the device cache."""
    get_device_manager().empty_cache()


def get_memory_usage() -> Dict[str, float]:
    """Get current memory usage."""
    return get_device_manager().get_memory_usage()


def set_device(device: torch.device) -> None:
    """
    Manually set the device (primarily for testing).
    
    Args:
        device: Device to set
    """
    global _device_manager
    with _device_lock:
        _device_manager = None  # Reset singleton
        # Create new instance with manual device
        _device_manager = DeviceManager()
        _device_manager._device = device
        _device_manager._device_type = DeviceType(device.type)
        logger.warning(f"Device manually set to: {device}")


# Initialize device manager on module import
def _initialize_device_on_import():
    """Initialize the device manager when the module is imported."""
    try:
        device_manager = get_device_manager()
        logger.info(f"PyMBO initialized with device: {device_manager.device}")
        
        # Log device capabilities
        info = device_manager.get_device_info()
        logger.info(f"Device capabilities: {info}")
        
    except Exception as e:
        logger.error(f"Failed to initialize device manager: {e}")


# Initialize on import
_initialize_device_on_import()