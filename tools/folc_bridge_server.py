#!/usr/bin/env python3
# FOLC Bridge Server (Device Side)
# Runs on Orbic Speed to replace ADB

import socket
import subprocess
import os
import struct
import sys
import threading

PORT = 5000
BUFFER_SIZE = 4096

def handle_client(conn, addr):
    print(f"Connection from {addr}")
    try:
        while True:
            # Read command length (4 bytes)
            header = conn.recv(4)
            if not header: break
            cmd_len = struct.unpack("!I", header)[0]
            
            # Read command
            cmd_data = b""
            while len(cmd_data) < cmd_len:
                chunk = conn.recv(min(BUFFER_SIZE, cmd_len - len(cmd_data)))
                if not chunk: break
                cmd_data += chunk
                
            if not cmd_data: break
            
            try:
                request = cmd_data.decode('utf-8').split(' ', 1)
                action = request[0]
                
                if action == "EXEC":
                    command = request[1]
                    print(f"Executing: {command}")
                    try:
                        # Run command
                        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                        response = b"OK" + output
                    except subprocess.CalledProcessError as e:
                        response = b"ERR" + e.output
                    except Exception as e:
                        response = b"ERR" + str(e).encode()
                        
                elif action == "PUSH":
                    # PUSH <path> <size>
                    meta, _ = request[1].split('\n', 1) # Metadata might have newline
                    dest_path, size_str = meta.split(' ')
                    file_size = int(size_str)
                    
                    print(f"Receiving file: {dest_path} ({file_size} bytes)")
                    
                    # Read file content
                    received = 0
                    with open(dest_path, 'wb') as f:
                        while received < file_size:
                            chunk = conn.recv(min(BUFFER_SIZE, file_size - received))
                            if not chunk: break
                            f.write(chunk)
                            received += len(chunk)
                            
                    response = b"OK"
                    
                else:
                    response = b"ERR Unknown Command"

            except Exception as e:
                response = b"ERR " + str(e).encode()

            # Send Response Length + Response
            conn.sendall(struct.pack("!I", len(response)))
            conn.sendall(response)
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(('0.0.0.0', PORT))
    s.listen(5)
    print(f"FOLC Bridge listening on 0.0.0.0:{PORT}")
    
    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn, addr))
        t.start()

if __name__ == "__main__":
    main()
