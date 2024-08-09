import socket
import os
import argparse

def display_routing_table():
    print("Routing Table")
    with open("/proc/net/route") as f:
        for line in f:
            print(line.strip())

def display_interface_table():
    print("Interface Table")
    with open("/proc/net/dev") as f:
        for line in f:
            print(line.strip())

def display_multicast_groups():
    print("Multicast Group Memberships")
    with open("/proc/net/igmp") as f:
        for line in f:
            print(line.strip())

def display_statistics():
    print("Networking Statistics")
    with open("/proc/net/snmp") as f:
        for line in f:
            print(line.strip())

def display_masquerade():
    print("Masqueraded Connections")
    with open("/proc/net/ip_conntrack") as f:
        for line in f:
            print(line.strip())

def main():

    parser = argparse.ArgumentParser(description="Raystat, Advanced network statistics tool for Bad Package Manager")
    
    parser.add_argument('-r', '--route', action='store_true', help='display routing table')
    parser.add_argument('-i', '--interfaces', action='store_true', help='display interface table')
    parser.add_argument('-g', '--groups', action='store_true', help='display multicast group memberships')
    parser.add_argument('-s', '--statistics', action='store_true', help='display networking statistics (like SNMP)')
    parser.add_argument('-M', '--masquerade', action='store_true', help='display masqueraded connections')


    # to be added
    #parser.add_argument('-v', '--verbose', action='store_true', help='be verbose')
    #parser.add_argument('-W', '--wide', action='store_true', help="don't truncate IP addresses")
    #parser.add_argument('-n', '--numeric', action='store_true', help="don't resolve names")
    #parser.add_argument('--numeric-hosts', action='store_true', help="don't resolve host names")
    #parser.add_argument('--numeric-ports', action='store_true', help="don't resolve port names")
    #parser.add_argument('--numeric-users', action='store_true', help="don't resolve user names")
    #parser.add_argument('-N', '--symbolic', action='store_true', help="resolve hardware names")
    #parser.add_argument('-e', '--extend', action='store_true', help='display other/more information')
    #parser.add_argument('-p', '--programs', action='store_true', help='display PID/Program name for sockets')
    #parser.add_argument('-o', '--timers', action='store_true', help='display timers')
    #parser.add_argument('-c', '--continuous', action='store_true', help='continuous listing')
    #
    #parser.add_argument('-l', '--listening', action='store_true', help='display listening server sockets')
    #parser.add_argument('-a', '--all', action='store_true', help='display all sockets (default: connected)')
    #parser.add_argument('-F', '--fib', action='store_true', help='display Forwarding Information Base (default)')
    #parser.add_argument('-C', '--cache', action='store_true', help='display routing cache instead of FIB')
    #parser.add_argument('-Z', '--context', action='store_true', help='display SELinux security context for sockets')

    args = parser.parse_args()

    if args.route:
        display_routing_table()
    if args.interfaces:
        display_interface_table()
    if args.groups:
        display_multicast_groups()
    if args.statistics:
        display_statistics()
    if args.masquerade:
        display_masquerade()
    if not args.route or args.interfaces or args.groups or args.statistics or args.masquerade:
        parser.print_help()

if __name__ == '__main__':
    main()
