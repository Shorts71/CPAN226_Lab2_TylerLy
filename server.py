# This program was modified by Tyler Ly / n01725055

import socket
import argparse
import struct

CHUNK_SIZE = 1024
EOF_SEQ = 0xFFFFFFFF

def run_server(port, output_file):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', port)
    print(f"[*] Server listening on port {port}")
    sock.bind(server_address)

    try:
        while True:
            print("==== Waiting for new file transfer ====")
            f = None
            expected_seq_num = 0
            buffer = {}
            while True:
                packet, addr = sock.recvfrom(CHUNK_SIZE + 4)
                if not packet:
                    continue
                seq_num = struct.unpack('!I', packet[:4])[0]
                data = packet[4:]
                if seq_num == EOF_SEQ:
                    print(f"[*] EOF received from {addr}")
                    break
                if f is None:
                    ip, sender_port = addr
                    sender_filename = f"received_{ip.replace('.', '_')}_{sender_port}.jpg"
                    f = open(sender_filename, 'wb')
                    print(f"[*] File opened for writing as '{sender_filename}'")
                sock.sendto(struct.pack('!I', seq_num), addr)
                if seq_num == expected_seq_num:
                    f.write(data)
                    expected_seq_num += 1
                    while expected_seq_num in buffer:
                        f.write(buffer.pop(expected_seq_num))
                        expected_seq_num += 1
                elif seq_num > expected_seq_num:
                    buffer[seq_num] = data
                else:
                    pass
            if f:
                f.close()
            print("==== End of reception ====")

    except KeyboardInterrupt:
        print("\n[!] Server stopped manually.")
    except Exception as e:
        print(f"[!] Error: {e}")
    finally:
        sock.close()
        print("[*] Server socket closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reliable UDP File Receiver")
    parser.add_argument("--port", type=int, default=12001, help="Port to listen on")
    parser.add_argument("--output", type=str, default="received_file.jpg", help="File path to save data")
    args = parser.parse_args()

    run_server(args.port, args.output)
