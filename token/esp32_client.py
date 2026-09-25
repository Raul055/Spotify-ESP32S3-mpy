import socket
import json

class esp32_handler():
    # -- Init class
    def __init__(self, debug=False) -> None:
        # ESP32 attribute
        self.device_ip = None
        self.debug = debug

    # -- Debugging print for debug flag
    def debug_print(self, *args):
        if self.debug:
            print(*args)

    # -- Push credentials into device
    def push_to_device(self, device_ip, port, values: dict, timeout=10):
        # Create a socket for connection
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        
        # Try to connect and send response
        try:
            s.connect((device_ip, port))
            s.send(json.dumps(values).encode())
            response = s.recv(1024).decode()
            return True
        
        # Something falied, error
        except Exception as e:
            print("Push failed:", e)
            return e

        # Finally close connection
        finally:
            s.close()

if __name__ == "__main__":
    pass