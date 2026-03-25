#!/usr/bin/env python3
"""
Standalone Codebase Analyzer CLI
Usage: python analyze_code.py <project_path>
"""

import sys
import os
from pathlib import Path
from collections import defaultdict
import ast


def analyze_directory(path: Path):
    stats = {
        'total_files': 0,
        'file_types': defaultdict(int),
        'total_lines': 0,
        'python_files': 0,
        'functions': defaultdict(list),  # mapping: relative_path -> [function names]
        'classes': defaultdict(list),    # mapping: relative_path -> [class names]
        'imports': set(),
        'files_detail': []  # list of dicts with keys: path, language, lines, functions, classes
    }

    skip_dirs = {
        '.git', '__pycache__', '.env', 'venv', 'node_modules',
        '.pytest_cache', 'uploads', 'dist', 'build'
    }

    for root, dirs, files in os.walk(path):
        # mutate dirs in-place to prevent walking into unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for fname in files:
            file_path = Path(root) / fname
            try:
                rel_path = str(file_path.relative_to(path))
            except Exception:
                rel_path = str(file_path)

            stats['total_files'] += 1
            ext = file_path.suffix.lower()
            stats['file_types'][ext] += 1

            if ext != '.py':
                continue

            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
            except (OSError, UnicodeDecodeError) as e:
                print(f"[WARN] Skipping unreadable file {file_path}: {e}")
                continue

            lines = content.splitlines()
            stats['total_lines'] += len(lines)
            stats['python_files'] += 1

            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                print(f"[WARN] Skipping file with syntax error {file_path}: {e}")
                continue

            funcs = []
            classes = []
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    funcs.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name:
                            stats['imports'].add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        stats['imports'].add(node.module.split('.')[0])

            if funcs:
                stats['functions'][rel_path].extend(funcs)
            if classes:
                stats['classes'][rel_path].extend(classes)

            stats['files_detail'].append({
                'path': rel_path,
                'language': 'Python',
                'lines': len(lines),
                'functions': len(funcs),
                'classes': len(classes)
            })

    return stats


def print_summary(path: Path, stats: dict):
    print("\n" + "=" * 80)
    print("[CODEBASE ANALYSIS]")
    print("=" * 80)
    print(f"Project: {path.name}")
    print(f"Path:    {path}")
    print("=" * 80)
    print(f"Total files scanned: {stats['total_files']}")
    print(f"Total lines (in .py files): {stats['total_lines']}")
    print(f"Python files: {stats['python_files']}")
    print(f"Unique imports used: {len(stats['imports'])}")
    if stats['imports']:
        print("Top imports:", ", ".join(sorted(stats['imports'])[:20]))
    print("\nFile type distribution:")
    for ext, count in sorted(stats['file_types'].items(), key=lambda x: (-x[1], x[0])):
        print(f"  {ext or '<no-ext>'}: {count}")
    print("\nSample Python files (by lines, top 10):")
    py_files = [f for f in stats['files_detail'] if f['language'] == 'Python']
    for info in sorted(py_files, key=lambda x: -x['lines'])[:10]:
        print(f"  {info['path']}: {info['lines']} lines, {info['functions']} funcs, {info['classes']} classes")
    print("\n" + "=" * 80 + "\n")


def main():
    if len(sys.argv) >= 2:
        project_path = Path(sys.argv[1])
    else:
        project_path = Path(__file__).parent
        print(f"[INFO] No path provided, analyzing script directory: {project_path}")

    if not project_path.exists():
        print(f"[ERROR] Path does not exist: {project_path}")
        return 1
    if not project_path.is_dir():
        print(f"[ERROR] Path is not a directory: {project_path}")
        return 1

    stats = analyze_directory(project_path)
    print_summary(project_path, stats)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())