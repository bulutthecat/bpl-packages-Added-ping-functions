# Copywright (c) 2024 Kevin Dalli
 
import socket
import struct
import time
import os

from check import checksum, anonymize_ip, validip

def create_packet(id):
    header = struct.pack("bbHHh", 8, 0, 0, id, 1)
    data = struct.pack("d", time.time())
    my_checksum = checksum(header + data)
    header = struct.pack("bbHHh", 8, 0, socket.htons(my_checksum), id, 1)
    return header + data

def traceroute(host, max_hops=30, obfuscate=False):

    # warn if the client is running Windows
    if "windows" in os.name:
        print("Warning: Traceroute may not work as expected on Windows")

    dest_addr = socket.gethostbyname(host)
    port = 33434
    timeout = 2.0
    ttl = 1

    if obfuscate:
        print(f"traceroute to {anonymize_ip(host)} ({anonymize_ip(dest_addr)}), {max_hops} hops max")
    else:
        print(f"traceroute to {host} ({dest_addr}), {max_hops} hops max")

    while True:
        recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP)
        send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
        recv_socket.settimeout(timeout)
        recv_socket.bind(("", port))

        packet_id = int((id(timeout) * time.time()) % 65535)
        packet = create_packet(packet_id)

        # bind the sending socket before sending data < this WILL throw an error on all platforms
        send_socket.bind(("", 0))
        send_socket.sendto(b'', (dest_addr, port))

        start_time = time.time()
        addr = None
        try:
            _, curr_addr = recv_socket.recvfrom(512)
            elapsed = (time.time() - start_time) * 1000
            addr = curr_addr[0]
            try:
                host = socket.gethostbyaddr(addr)[0]
            except socket.error:
                host = addr
        except socket.error:
            elapsed = timeout * 1000
        finally:
            send_socket.close()
            recv_socket.close()

        if addr and obfuscate:
            if validip(host):
                print(f"{ttl}\t{elapsed:.3f} ms\t{anonymize_ip(host)} ({anonymize_ip(addr)})")
        elif addr and not validip(host):
            print(f"{ttl}\t{elapsed:.3f} ms\t{host} ({addr})")
        else:
            print(f"{ttl}\t*\tRequest timed out")

        ttl += 1
        if addr == dest_addr or ttl > max_hops:
            break