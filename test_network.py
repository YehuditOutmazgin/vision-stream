"""Test network connectivity to RTSP servers"""
import socket
import sys

def test_connection(host, port):
    """Test TCP connection to host:port"""
    print(f"\nTesting {host}:{port}...")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((host, port))
        sock.close()
        
        if result == 0:
            print(f"[OK] Port {port} is open on {host}")
            return True
        else:
            print(f"[FAIL] Port {port} is closed/filtered on {host}")
            return False
    except socket.gaierror:
        print(f"[FAIL] Cannot resolve hostname {host}")
        return False
    except Exception as e:
        print(f"[FAIL] {e}")
        return False

# Test RTSP servers
print("=" * 60)
print("Testing RTSP Server Connectivity")
print("=" * 60)

servers = [
    ("rtsp.stream", 554),
    ("wowzaec2demo.streamlock.net", 554),
    ("google.com", 80),  # Control test - should work
]

for host, port in servers:
    test_connection(host, port)

print("\n" + "=" * 60)
print("If Google works but RTSP doesn't, your firewall blocks RTSP")
print("=" * 60)
