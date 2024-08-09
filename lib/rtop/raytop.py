import os
import time
import curses

def get_process_list():
    process_list = []
    for subdir in os.listdir('/proc'):
        if subdir.isdigit():
            pid = subdir
            try:
                with open(os.path.join('/proc', subdir, 'stat'), 'r') as f:
                    data = f.read().split()
                    with open(os.path.join('/proc', subdir, 'cmdline'), 'r') as cmdf:
                        cmd = cmdf.read().replace('\0', ' ').strip()
                    process_list.append({
                        'pid': int(pid),
                        'name': data[1].strip('()'),
                        'cpu_time': int(data[13]) + int(data[14]),
                        'cmd': cmd
                    })
            except IOError:
                continue
    return process_list

def get_memory_info():
    with open('/proc/meminfo', 'r') as f:
        lines = f.readlines()
    meminfo = {}
    for line in lines:
        parts = line.split()
        meminfo[parts[0].strip(':')] = int(parts[1])
    return meminfo

def get_cpu_usage():
    with open('/proc/stat', 'r') as f:
        lines = f.readlines()
    cpus = []
    for line in lines:
        if line.startswith('cpu') and line[3].isdigit():
            parts = line.split()
            if len(parts) >= 5:
                cpus.append({
                    'user': int(parts[1]),
                    'nice': int(parts[2]),
                    'system': int(parts[3]),
                    'idle': int(parts[4])
                })
    return cpus

def calculate_cpu_usage(prev, curr):
    usage = []
    for p, c in zip(prev, curr):
        prev_idle = p['idle']
        idle = c['idle']

        prev_non_idle = p['user'] + p['nice'] + p['system']
        non_idle = c['user'] + c['nice'] + c['system']

        prev_total = prev_idle + prev_non_idle
        total = idle + non_idle

        totald = total - prev_total
        idled = idle - prev_idle

        cpu_percentage = (totald - idled) / totald if totald > 0 else 0
        usage.append(cpu_percentage * 100)
    return usage

def display_top(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(1000)

    prev_cpu = get_cpu_usage()
    time.sleep(1)

    while True:
        stdscr.clear()

        try:
            process_list = sorted(get_process_list(), key=lambda x: x['cpu_time'], reverse=True)
            meminfo = get_memory_info()
            curr_cpu = get_cpu_usage()
            cpu_usage = calculate_cpu_usage(prev_cpu, curr_cpu)
            prev_cpu = curr_cpu
        except Exception as e:
            stdscr.addstr(0, 0, f"Error: {str(e)}")
            stdscr.refresh()
            continue

        stdscr.addstr(0, 0, f"{'PID':>5} {'Name':<20} {'CPU Time':>10} {'Command':<20}")
        
        for i, proc in enumerate(process_list[:10], start=1):
            stdscr.addstr(i, 0, f"{proc['pid']:>5} {proc['name']:<20} {proc['cpu_time']:>10} {proc['cmd'][:20]:<20}")

        mem_total = meminfo.get('MemTotal', 0)
        mem_free = meminfo.get('MemFree', 0)
        swap_total = meminfo.get('SwapTotal', 0)
        swap_free = meminfo.get('SwapFree', 0)
        mem_used = mem_total - mem_free
        swap_used = swap_total - swap_free

        stdscr.addstr(12, 0, f"Memory Usage: {mem_used / 1024:.2f}MB / {mem_total / 1024:.2f}MB")
        stdscr.addstr(13, 0, f"Swap Usage: {swap_used / 1024:.2f}MB / {swap_total / 1024:.2f}MB")

        max_y, max_x = stdscr.getmaxyx()
        bar_width = max_x - 20  # Ensure the bar width fits in the window

        for idx, usage in enumerate(cpu_usage):
            if 15 + idx >= max_y - 1:
                break
            bar_length = min(bar_width, int(usage / 2))
            bar = '#' * bar_length + ' ' * (bar_width - bar_length)
            stdscr.addstr(15 + idx, 0, f"CPU {idx}: [{bar}] {usage:.2f}%")

        stdscr.refresh()

        if stdscr.getch() == ord('q'):
            break

def main():
    curses.wrapper(display_top)

if __name__ == "__main__":
    main()
