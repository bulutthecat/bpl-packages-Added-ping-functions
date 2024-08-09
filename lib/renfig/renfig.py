import os
import sys
import argparse

badnet_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'badnet')) # use the badnet module, from within lib, given it is installed correctly
sys.path.append(badnet_path)

from badnet import list_interfaces, get_interface_info

def main():

    parser = argparse.ArgumentParser(description='rayconfig, simplified ifconfig for Bad Package Manager.')
    
    parser.parse_args()

    interfaces = list_interfaces()
    for interface in interfaces:
        info = get_interface_info(interface)
        print(f"Interface: {info['interface']}")
        print(f"  IP Address: {info['ip_address']}")
        print(f"  Netmask: {info['netmask']}")
        print(f"  MAC Address: {info['mac_address']}")
        print()

if __name__ == "__main__":
    main()
