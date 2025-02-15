import socket

# Create a socket to determine the local IP address
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    s.connect(("8.8.8.8", 80))  # Connecting to a public DNS server to get the real local IP
    IP_ADDRESS = s.getsockname()[0]
except Exception:
    IP_ADDRESS = "127.0.0.1"
finally:
    s.close()

# Export the IP address as a constant
__all__ = ["IP_ADDRESS"]