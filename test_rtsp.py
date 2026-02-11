"""Test RTSP connection with ffprobe"""
import subprocess
import sys

rtsp_url = "rtsp://rtsp.stream/pattern"

print(f"Testing RTSP URL: {rtsp_url}")
print("=" * 50)

try:
    # Try with ffprobe (comes with PyAV)
    result = subprocess.run(
        ["ffprobe", "-rtsp_transport", "tcp", "-i", rtsp_url],
        capture_output=True,
        text=True,
        timeout=5
    )
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)
    print("Return code:", result.returncode)
except FileNotFoundError:
    print("ffprobe not found - trying with av directly")
    import av
    try:
        container = av.open(rtsp_url, options={'rtsp_transport': 'tcp'}, timeout=(3, 3))
        print(f"SUCCESS! Streams: {len(container.streams.video)}")
        container.close()
    except Exception as e:
        print(f"FAILED: {e}")
except subprocess.TimeoutExpired:
    print("TIMEOUT - URL not responding")
except Exception as e:
    print(f"ERROR: {e}")
