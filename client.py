# This program was modified by Tyler Ly / n01725055

import socket
import argparse
import time
import os
import struct

CHUNK_SIZE = 1024
EOF_SEQ = 0xFFFFFFFF

def run_client(target_ip, target_port, input_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    base_timeout = 1.0
    sock.settimeout(base_timeout)
    server_address = (target_ip, target_port)

    print(f"[*] Sending file '{input_file}' to {target_ip}:{target_port}")

    if not os.path.exists(input_file):
        print(f"[!] Error: File '{input_file}' not found.")
        return

    try:
        with open(input_file, 'rb') as f:
            sequence_number = 0

            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                header = struct.pack('!I', sequence_number)
                packet = header + chunk

                ack_received = False
                timeout_multiplier = 1.0
                while not ack_received:
                    sock.sendto(packet, server_address)
                    current_timeout = base_timeout * timeout_multiplier
                    sock.settimeout(current_timeout)
                    try:
                        ack_data, _ = sock.recvfrom(4)
                        ack_num = struct.unpack('!I', ack_data)[0]
                        if ack_num == sequence_number:
                            ack_received = True
                            sequence_number += 1
                            timeout_multiplier = 1.0
                    except socket.timeout:
                        print(f"[!] Timeout for packet {sequence_number}, resending...")
                        timeout_multiplier = min(timeout_multiplier * 1.5, 5.0)

        eof_packet = struct.pack('!I', EOF_SEQ)
        sock.sendto(eof_packet, server_address)
        print("[*] File transmission complete.")

    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Sender")
    parser.add_argument("--target_ip", type=str, default="127.0.0.1", help="Destination IP (Relay or Server)")
    parser.add_argument("--target_port", type=int, default=12000, help="Destination Port")
    parser.add_argument("--file", type=str, required=True, help="Path to file to send")
    args = parser.parse_args()

    run_client(args.target_ip, args.target_port, args.file)
