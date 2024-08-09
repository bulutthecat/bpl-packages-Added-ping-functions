import argparse
import os
import sys

# This throws errors, dont know why, it works fine!

badnet_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'badnet')) # use the badnet module, from within lib, given it is installed correctly
sys.path.append(badnet_path)

from badnet import HttpClient, FtpClient

def main():
    parser = argparse.ArgumentParser(description='RayCurl, fully rewritten CURL to support Bad Package Manager.')
    
    parser.add_argument('url', help='The URL to fetch.')
    parser.add_argument('-d', '--data', help='HTTP POST data')
    parser.add_argument('-f', '--fail', action='store_true', help='Fail fast with no output on HTTP errors')
    parser.add_argument('-i', '--include', action='store_true', help='Include response headers in output')
    parser.add_argument('-o', '--output', help='Write to file instead of stdout')
    parser.add_argument('-O', '--remote-name', action='store_true', help='Write output to file named as remote file')
    parser.add_argument('-s', '--silent', action='store_true', help='Silent mode')
    parser.add_argument('-T', '--upload-file', help='Transfer local FILE to destination')
    parser.add_argument('-u', '--user', help='Server user and password')
    parser.add_argument('-A', '--user-agent', help='Send User-Agent <name> to server')
    parser.add_argument('-v', '--verbose', action='store_true', help='Make the operation more talkative')
    parser.add_argument('-V', '--version', action='store_true', help='Show version number and quit')

    args = parser.parse_args()

    if args.version:
        print("Python curl version 1.0")
        sys.exit(0)

    headers = {}
    if args.user_agent:
        headers['User-Agent'] = args.user_agent

    auth = None
    if args.user:
        auth = tuple(args.user.split(':'))

    parsed_url = urllib.parse.urlparse(args.url)
    
    if parsed_url.scheme in ['http', 'https']:
        http_client = HttpClient(args.url)
        
        if args.upload_file:
            with open(args.upload_file, 'rb') as f:
                files = {'file': f}
                status, content = http_client.post(parsed_url.path, files, headers=headers)
        else:
            if args.data:
                status, content = http_client.post(parsed_url.path, data=args.data, headers=headers)
            else:
                status, content = http_client.get(parsed_url.path, headers=headers)
                
        if args.fail and status >= 400:
            sys.exit(1)
        
        output = ""
        if args.include:
            output += f"HTTP/1.1 {status} {http.client.responses[status]}\n"
            for key, value in response.headers.items():
                output += f"{key}: {value}\n"
            output += "\n"
        
        output += content.decode()

        if not args.silent:
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
            elif args.remote_name:
                remote_filename = os.path.basename(parsed_url.path)
                with open(remote_filename, 'w') as f:
                    f.write(output)
            else:
                print(output)
        
        http_client.close()

    elif parsed_url.scheme == 'ftp':
        ftp_client = FtpClient(parsed_url.hostname, user=args.user.split(':')[0], passwd=args.user.split(':')[1])
        ftp_client.login()
        
        if args.upload_file:
            ftp_client.upload_file(args.upload_file, parsed_url.path)
        else:
            if args.output:
                ftp_client.download_file(parsed_url.path, args.output)
            elif args.remote_name:
                remote_filename = os.path.basename(parsed_url.path)
                ftp_client.download_file(parsed_url.path, remote_filename)
            else:
                local_filename = os.path.basename(parsed_url.path)
                ftp_client.download_file(parsed_url.path, local_filename)
        
        ftp_client.close()
    
if __name__ == "__main__":
    main()
