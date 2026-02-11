"""
Webcam Utilities - Enumerate and detect available webcams on Windows.
"""

import platform
from typing import List
from utils.logger import get_logger

logger = get_logger()


def get_available_webcams() -> List[str]:
    """
    Get list of available webcam names on Windows.
    
    Returns:
        List of webcam device names
    """
    if platform.system() != 'Windows':
        logger.log_error("WEBCAM_ENUM", "Webcam enumeration only supported on Windows")
        return []
    
    try:
        import wmi
        c = wmi.WMI()
        devices = []
        
        # Query for PnP devices with Camera class
        for item in c.Win32_PnPEntity():
            if item.PNPClass == 'Camera' and item.Status == 'OK':
                devices.append(item.Caption)
        
        logger.log_ui_event(f"Found {len(devices)} webcam(s): {devices}")
        return devices
        
    except ImportError:
        logger.log_error("WEBCAM_ENUM", "WMI module not available. Install with: pip install WMI")
        # Fallback: return common camera name
        return ["Integrated Camera"]
    except Exception as e:
        logger.log_error("WEBCAM_ENUM", f"Error enumerating webcams: {e}")
        # Fallback: return common camera name
        return ["Integrated Camera"]


def get_default_webcam() -> str:
    """
    Get the default webcam device name.
    
    Returns:
        Default webcam name or empty string if none found
    """
    devices = get_available_webcams()
    if devices:
        return f"video={devices[0]}"
    return ""
