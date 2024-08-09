import os

def get_filesystem_info():
    usage_info = []
    
    with open('/proc/mounts', 'r') as f:
        for line in f:
            parts = line.split()
            device = parts[0]
            mountpoint = parts[1]
            
            if os.path.ismount(mountpoint):
                stat = os.statvfs(mountpoint)
                total = stat.f_blocks * stat.f_frsize
                available = stat.f_bavail * stat.f_frsize
                used = total - available
                if used != 0 and total != 0:
                
                    usage_info.append({
                        'Filesystem': device,
                        '1K-blocks': total // 1024,
                        'Used': used // 1024,
                        'Available': available // 1024,
                        'Use%': f"{used * 100 // total}%",
                        'Mounted on': mountpoint
                    })
                else:
                    usage_info.append({
                        'Filesystem': device,
                        '1K-blocks': total // 1024,
                        'Used': used // 1024,
                        'Available': available // 1024,
                        'Use%': f"{used}%",
                        'Mounted on': mountpoint
                    })
    
    return usage_info

def print_filesystem_info():
    headers = ['Filesystem', '1K-blocks', 'Used', 'Available', 'Use%', 'Mounted on']
    info = get_filesystem_info()
    
    # Calculate the maximum width for each column
    max_widths = {header: max(len(header), *(len(str(row[header])) for row in info)) for header in headers}
    
    # Print the headers
    print('  '.join(header.ljust(max_widths[header]) for header in headers))
    
    # Print the information
    for row in info:
        print('  '.join(str(row[header]).ljust(max_widths[header]) for header in headers))

if __name__ == "__main__":
    print_filesystem_info()