import socket
import time

def set_all_zero(IP: str, PORT: int, wait=0.1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((IP, PORT))
            for i in range(7):
                sensor_num = i+1
                command = f"SW,{sensor_num},001,+000000001\r\n"
                s.sendall(command.encode())
                time.sleep(wait)
                print(s.recv(1024).decode().strip())
            return True
    except Exception as e:
        print(f"TCP Error: {e}" )
        return False

def Read_all_sensor(IP: str, PORT: int, wait=0.1):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(3)
            s.connect((IP, PORT))
            s.sendall(b'M0\r\n')
            time.sleep(wait)
            return s.recv(1024).decode().strip()
    except Exception as e:
        print(f"TCP Error: {e}")   
        return False