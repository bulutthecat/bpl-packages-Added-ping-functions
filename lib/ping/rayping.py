# Copywright (c) 2024 Kevin Dalli

import os
import socket
import struct
import time
import select
import argparse
import sys

from check import checksum, xor_encrypt_decrypt, anonymize_ip, whois_query
from traceroute import traceroute

ICMP_ECHO_REQUEST = 8
ICMP_TIME_EXCEEDED = 11
ICMP_DEST_UNREACH = 3
ICMP_PORT_UNREACH = 3
VERSION = "1.3"

def create_packet(id, packet_size, pattern, key=None):
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, 0, id, 1)
    bytes_in_double = struct.calcsize('d')
    if pattern:
        data = pattern[:packet_size - bytes_in_double]
    else:
        data = (packet_size - bytes_in_double) * b'Q'

    data = struct.pack('d', time.time()) + data
    if key:
        data = xor_encrypt_decrypt(data, key)

    my_checksum = checksum(header + data)
    header = struct.pack('bbHHh', ICMP_ECHO_REQUEST, 0, socket.htons(my_checksum), id, 1)
    return header + data

def do_one_ping(dest_addr, timeout, ttl, packet_size, pattern, key):
    icmp = socket.getprotobyname("icmp")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    except PermissionError as e:
        print("Operation not permitted. Run as root or higher level user.")
        return None

    my_id = os.getpid() & 0xFFFF
    packet = create_packet(my_id, packet_size, pattern, key)

    while packet:
        sent = sock.sendto(packet, (dest_addr, 1))
        packet = packet[sent:]

    delay = receive_one_ping(sock, my_id, time.time(), timeout, dest_addr, key, packet_size)
    sock.close()
    return delay

def receive_one_ping(sock, id, time_sent, timeout, dest_addr, key, packet_size):
    time_left = timeout
    while True:
        started_select = time.time()
        what_ready = select.select([sock], [], [], time_left)
        how_long_in_select = (time.time() - started_select)
        if what_ready[0] == []:
            return None

        time_received = time.time()
        rec_packet, addr = sock.recvfrom(1024)

        icmp_header = rec_packet[20:28]
        type, code, checksum, packet_id, sequence = struct.unpack('bbHHh', icmp_header)

        if packet_id == id:
            bytes_in_double = struct.calcsize('d')
            data = rec_packet[28:28 + bytes_in_double + packet_size - bytes_in_double]
            if key:
                data = xor_encrypt_decrypt(data, key)
            time_sent = struct.unpack('d', data[:bytes_in_double])[0]
            return time_received - time_sent

        time_left = time_left - how_long_in_select
        if time_left <= 0:
            return None

def ping(host, count, interval, interface, ttl, packet_size, timeout, quiet, audible, timestamp, numeric, pattern, key, anonymize, auto_traceroute):
    dest = socket.gethostbyname(host)
    display_dest = anonymize_ip(dest) if anonymize else dest
    print(f'Pinging {display_dest} ({host}) > {packet_size} bytes of data:')

    if interface:
        print(f"Using interface: {interface}")

    sent_packets = 0
    received_packets = 0

    try:
        for i in range(count):
            sent_packets += 1
            delay = do_one_ping(dest, timeout, ttl, packet_size, pattern, key)
            if delay is None:
                if not quiet:
                    print(f'Ping to {display_dest} timed out')
                if auto_traceroute:
                    print("Performing traceroute...")
                    traceroute(host, max_hops=10)
                    break
            else:
                received_packets += 1
                delay = delay * 1000
                if not quiet:
                    line = f'Ping to {display_dest} took {delay:.2f} ms'
                    if timestamp:
                        line = f'[{time.time()}] {line}'
                    print(line)
                if audible:
                    print('\a', end='')

            time.sleep(interval)
        
        loss = sent_packets - received_packets
        print(f"Ping statistics for {display_dest}:")
        print(f"    Packets: Sent = {sent_packets}, Received = {received_packets}, Lost = {loss} ({(loss / sent_packets) * 100:.2f}% loss)")

    except KeyboardInterrupt:
        print("\nPing stopped.")
        loss = sent_packets - received_packets
        print(f"Ping statistics for {display_dest}:")
        print(f"    Packets: Sent = {sent_packets}, Received = {received_packets}, Lost = {loss} ({(loss / sent_packets) * 100:.2f}% loss)")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ping a host.')
    parser.add_argument('host', type=str, nargs='?', help='The host to ping.')
    parser.add_argument('-c', '--count', type=int, default=4, help='Stop after sending (and receiving) count ECHO_RESPONSE packets.')
    parser.add_argument('-i', '--interval', type=int, default=1, help='Wait interval seconds between sending each packet.')
    parser.add_argument('-I', '--interface', type=str, help='Specify a network interface to use for sending packets.')
    parser.add_argument('-t', '--ttl', type=int, default=64, help='Set the IP Time to Live.')
    parser.add_argument('-s', '--packetsize', type=int, default=56, help='Specify the number of data bytes to be sent.')
    parser.add_argument('-W', '--timeout', type=int, default=1, help='Time to wait for a response, in seconds.')
    parser.add_argument('-q', '--quiet', action='store_true', help='Quiet output. Only summary lines at startup and finish will be printed.')
    parser.add_argument('-a', '--audible', action='store_true', help='Beep when a packet is received.')
    parser.add_argument('-V', '--version', action='store_true', help='Print version and exit.')
    parser.add_argument('-D', '--timestamp', action='store_true', help='Print timestamp before each line.')
    parser.add_argument('-n', '--numeric', action='store_true', help='Numeric output only. No attempt to lookup symbolic names for host addresses.')
    parser.add_argument('-p', '--pattern', type=str, help='Specify up to 16 pattern bytes to fill out the packet you send.')
    parser.add_argument('-En', '--encrypt', type=str, help='Use the specified key to encrypt the payload of ICMP packets.')
    parser.add_argument('-An', '--anonymize', action='store_true', help='Anonymize source and destination IP addresses in logs and outputs.')
    parser.add_argument('-aTr', '--auto-traceroute', action='store_true', help='Perform a traceroute if the ping fails.')
    parser.add_argument('-Tr', '--traceroute', action='store_true', help='Perform a traceroute on the IP.')
    parser.add_argument('-Wh', '--whois', action='store_true', help='Perform a whois query on the IP.')

    # WHOIS options
    parser.add_argument('-Wl', '--levelonespecific', action='store_true', help='WHOIS: Find the one level less specific match.')
    parser.add_argument('-WL', '--alllevelspecific', action='store_true', help='WHOIS: Find all levels less specific matches.')
    parser.add_argument('-Wm', '--levelmore', action='store_true', help='WHOIS: Find all one level more specific matches.')
    parser.add_argument('-WM', '--alllevelsmore', action='store_true', help='WHOIS: Find all levels of more specific matches.')
    parser.add_argument('-Wc', '--smallest', action='store_true', help='WHOIS: Find the smallest match containing a mnt-irt attribute.')
    parser.add_argument('-Wx', '--exact', action='store_true', help='WHOIS: Exact match.')
    parser.add_argument('-Wb', '--brief', action='store_true', help='WHOIS: Return brief IP address ranges with abuse contact.')
    parser.add_argument('-WB', '--no_filter', action='store_true', help='WHOIS: Turn off object filtering (show email addresses).')
    parser.add_argument('-WG', '--no_grouping', action='store_true', help='WHOIS: Turn off grouping of associated objects.')
    parser.add_argument('-Wd', '--reverse', action='store_true', help='WHOIS: Return DNS reverse delegation objects too.')
    parser.add_argument('-Wi', '--inverse_attrs', type=str, help='WHOIS: Do an inverse look-up for specified attributes.')
    parser.add_argument('-WT', '--types', type=str, help='WHOIS: Only look for objects of specified types.')
    parser.add_argument('-WK', '--primary_keys', action='store_true', help='WHOIS: Only primary keys are returned.')
    parser.add_argument('-Wr', '--no_recursive', action='store_true', help='WHOIS: Turn off recursive look-ups for contact information.')
    parser.add_argument('-WR', '--force_local', action='store_true', help='WHOIS: Show local copy of the domain object even if it contains referral.')
    parser.add_argument('-Wa', '--all_databases', action='store_true', help='WHOIS: Also search all the mirrored databases.')
    parser.add_argument('-Ws', '--sources', type=str, help='WHOIS: Search the database mirrored from specified sources.')
    parser.add_argument('-Wg', '--updates', type=str, help='WHOIS: Find updates from source from serial FIRST to LAST.')
    parser.add_argument('-Wt', '--template_type', type=str, help='WHOIS: Request template for object of specified type.')
    parser.add_argument('-Wv', '--verbose_type', type=str, help='WHOIS: Request verbose template for object of specified type.')
    parser.add_argument('-Wq', '--server_info', type=str, help='WHOIS: Query specified server info.')

    """
            domain (str): The domain to query.
        levelonespecific (bool): -Wl  Find the one level less specific match.
        alllevelspecific (bool): -WL  Find all levels less specific matches.
        levelmore (bool): -Wm  Find all one level more specific matches.
        alllevelsmore (bool): -WM  Find all levels of more specific matches.
        smallest (bool): -Wc  Find the smallest match containing a mnt-irt attribute.
        exact (bool): -Wx  Exact match.
        brief (bool): -Wb  Return brief IP address ranges with abuse contact.
        no_filter (bool): -WB  Turn off object filtering (show email addresses).
        no_grouping (bool): -WG  Turn off grouping of associated objects.
        reverse (bool): -Wd  Return DNS reverse delegation objects too.
        inverse_attrs (list): -Wi ATTR[,ATTR]...  Do an inverse look-up for specified attributes.
        types (list): -WT TYPE[,TYPE]...  Only look for objects of specified types.
        primary_keys (bool): -WK  Only primary keys are returned.
        no_recursive (bool): -Wr  Turn off recursive look-ups for contact information.
        force_local (bool): -WR  Show local copy of the domain object even if it contains referral.
        all_databases (bool): -Wa  Also search all the mirrored databases.
        sources (list): -Ws SOURCE[,SOURCE]...  Search the database mirrored from specified sources.
        updates (str): -Wg SOURCE:FIRST-LAST  Find updates from source from serial FIRST to LAST.
        template_type (str): -Wt TYPE  Request template for object of specified type.
        verbose_type (str): -Wv TYPE  Request verbose template for object of specified type.
        server_info (str): -Wq [version|sources|types]  Query specified server info.
    """

    args = parser.parse_args()
    inverse_attrs = args.inverse_attrs.split(',') if args.inverse_attrs else None
    types = args.types.split(',') if args.types else None
    sources = args.sources.split(',') if args.sources else None

    if args.version:
        print(f"Ping version {VERSION}")
    elif args.whois:
        
        result = whois_query(args.host, levelonespecific=args.levelonespecific, alllevelspecific=args.alllevelspecific, 
                          levelmore=args.levelmore, alllevelsmore=args.alllevelsmore, smallest=args.smallest, exact=args.exact, 
                          brief=args.brief, no_filter=args.no_filter, no_grouping=args.no_grouping, reverse=args.reverse, 
                          inverse_attrs=inverse_attrs, types=types, primary_keys=args.primary_keys, no_recursive=args.no_recursive, 
                          force_local=args.force_local, all_databases=args.all_databases, sources=sources, updates=args.updates, 
                          template_type=args.template_type, verbose_type=args.verbose_type, server_info=args.server_info)
        print(result)

    elif args.traceroute and args.host:
        if args.anonymize:
            traceroute(args.host, obfuscate=True)
            sys.exit
        else:
            traceroute(args.host)
    elif not args.host:
        parser.print_help()
    else:
        ping(args.host, args.count, args.interval,
                args.interface, args.ttl, args.packetsize,
                args.timeout, args.quiet, args.audible, 
                args.timestamp, args.numeric, 
                args.pattern.encode() if args.pattern else None, 
                args.encrypt, args.anonymize, args.auto_traceroute)
