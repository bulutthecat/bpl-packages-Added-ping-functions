# Copywright (c) 2024 Kevin Dalli
 
import itertools
import hashlib
import socket

def checksum(source_string):
    sum = 0
    countTo = (len(source_string) // 2) * 2
    count = 0

    while count < countTo:
        thisVal = source_string[count + 1] * 256 + source_string[count]
        sum = sum + thisVal
        sum = sum & 0xffffffff
        count = count + 2

    if countTo < len(source_string):
        sum = sum + source_string[len(source_string) - 1]
        sum = sum & 0xffffffff

    sum = (sum >> 16) + (sum & 0xffff)
    sum = sum + (sum >> 16)
    answer = ~sum
    answer = answer & 0xffff
    answer = answer >> 8 | (answer << 8 & 0xff00)
    return answer

def xor_encrypt_decrypt(data, key):
    return bytes(a ^ b for a, b in zip(data, itertools.cycle(key.encode())))
import hashlib

def anonymize_ip(ip):
    ip_hash = hashlib.md5(ip.encode()).hexdigest()
    ip_hash = ip_hash[:8]
    anonymized_ip = ''
    for char in ip_hash:
        if char.isdigit():
            anonymized_ip += chr(ord('a') + int(char))
        else:
            anonymized_ip += chr(ord('k') + ord(char) - ord('a'))

    return anonymized_ip

def validip(ip):
    # to differentiate between hostnames and IP addresses
    # if the text has three or more dots AND it has no letters, it's an IP address
    # if it is a valid IP, return true, if not, return false
    return ip.count('.') >= 3 and not any(c.isalpha() for c in ip)

def whois_query(domain, levelonespecific=False, alllevelspecific=False, levelmore=False, alllevelsmore=False,
                smallest=False, exact=False, brief=False, no_filter=False, no_grouping=False, reverse=False,
                inverse_attrs=None, types=None, primary_keys=False, no_recursive=False, force_local=False,
                all_databases=False, sources=None, updates=None, template_type=None, verbose_type=None,
                server_info=None):
    server = 'whois.verisign-grs.com'  # default whois server for .com and .net domains
    port = 43
    
    options = []
    if levelonespecific:
        options.append('-l')
    if alllevelspecific:
        options.append('-L')
    if levelmore:
        options.append('-m')
    if alllevelsmore:
        options.append('-M')
    if smallest:
        options.append('-c')
    if exact:
        options.append('-x')
    if brief:
        options.append('-b')
    if no_filter:
        options.append('-B')
    if no_grouping:
        options.append('-G')
    if reverse:
        options.append('-d')
    if inverse_attrs:
        options.append(f"-i {','.join(inverse_attrs)}")
    if types:
        options.append(f"-T {','.join(types)}")
    if primary_keys:
        options.append('-K')
    if no_recursive:
        options.append('-r')
    if force_local:
        options.append('-R')
    if all_databases:
        options.append('-a')
    if sources:
        options.append(f"-s {','.join(sources)}")
    if updates:
        options.append(f"-g {updates}")
    if template_type:
        options.append(f"-t {template_type}")
    if verbose_type:
        options.append(f"-v {verbose_type}")
    if server_info:
        options.append(f"-q {server_info}")

    query = f"{domain}\r\n" + " ".join(options) + "\r\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((server, port))
        s.sendall((query + '\r\n').encode())

        response = b''
        while True:
            data = s.recv(4096)
            if not data:
                break
            response += data

    return response.decode()