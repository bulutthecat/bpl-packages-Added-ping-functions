# Copyright (C) Kevin Dalli 2024

import os
import argparse

def find_files(base_dir, mindepth=0, maxdepth=float('inf'), xdev=False, mount=False):
    results = []
    for root, dirs, files in os.walk(base_dir, topdown=True, followlinks=True):
        depth = root[len(base_dir):].count(os.sep)
        if mindepth <= depth <= maxdepth:
            results.extend([os.path.join(root, name) for name in files])
        if xdev or mount:
            dirs[:] = [d for d in dirs if os.path.samefile(base_dir, os.path.join(root, d))]
        
        if depth >= maxdepth:
            dirs[:] = []
    return results

def main():
    parser = argparse.ArgumentParser(description='Basic find utility in Python.')
    parser.add_argument('path', help='Path to start searching from.', type=str)
    parser.add_argument('-mindepth', type=int, default=0, help='Minimum depth of directories to include.')
    parser.add_argument('-maxdepth', type=int, default=float('inf'), help='Maximum depth of directories to include.')
    parser.add_argument('-xdev', action='store_true', help='Stay on the same file system.')
    parser.add_argument('-mount', action='store_true', help='Stay on the same mount point.')
    parser.add_argument('-name', type=str, help='Pattern to match filenames.')
    
    args = parser.parse_args()
    base_dir = os.path.normpath(args.path)

    results = find_files(base_dir, mindepth=args.mindepth, maxdepth=args.maxdepth, xdev=args.xdev, mount=args.mount)
    
    if args.name:
        results = [file for file in results if os.path.basename(file) == args.name]

    for result in results:
        print(result)

if __name__ == "__main__":
    main()