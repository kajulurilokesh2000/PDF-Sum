#!/usr/bin/env python3
"""
PDF Codebase Analyzer - Hardcoded for PDF folder
Run: python analyze_pdf.py
"""

import sys
import os
from pathlib import Path
from collections import Counter
import ast


def analyze_project(path: Path):
    if not path.exists():
        print(f"[ERROR] Path does not exist: {path}")
        return 1

    skip_dirs = {
        '.git', '__pycache__', '.env', 'venv', 'node_modules',
        '.pytest_cache', 'uploads', 'dist', 'build'
    }

    total_files = 0
    total_lines = 0
    file_type_counts = Counter()
    python_file_count = 0
    imports = set()
    functions_by_file = {}
    classes_by_file = {}
    files_detail = []

    for root, dirs, files in os.walk(path, topdown=True):
        # Filter out directories to skip
        dirs[:] = [d for d in dirs if d not in skip_dirs]

        for filename in files:
            total_files += 1
            file_path = Path(root) / filename
            rel_path = file_path.relative_to(path) if path in file_path.parents or file_path == path else file_path
            ext = file_path.suffix.lower()
            file_type_counts[ext] += 1

            if ext != '.py':
                continue

            try:
                with file_path.open('r', encoding='utf-8', errors='replace') as fh:
                    content = fh.read()
            except (OSError, UnicodeError) as e:
                print(f"[WARNING] Could not read {file_path}: {e}")
                continue

            lines = content.count('\n') + (0 if content.endswith('\n') or content == "" else 1)
            total_lines += lines

            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                print(f"[WARNING] Syntax error parsing {file_path}: {e}")
                # Still record line count and skip AST details for this file
                files_detail.append({
                    'path': str(rel_path),
                    'language': 'Python',
                    'lines': lines,
                    'functions': 0,
                    'classes': 0
                })
                continue

            funcs = []
            clss = []
            for node in ast.walk(tree):
                # Function (including async)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    if getattr(node, 'name', None):
                        funcs.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    if getattr(node, 'name', None):
                        clss.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name:
                            imports.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.add(node.module.split('.')[0])

            functions_by_file[str(rel_path)] = funcs
            classes_by_file[str(rel_path)] = clss
            python_file_count += 1
            files_detail.append({
                'path': str(rel_path),
                'language': 'Python',
                'lines': lines,
                'functions': len(funcs),
                'classes': len(clss)
            })

    # Summaries
    total_functions = sum(len(v) for v in functions_by_file.values())
    total_classes = sum(len(v) for v in classes_by_file.values())

    # Print results
    print("\n" + "=" * 80)
    print("[PDF CODEBASE ANALYSIS]")
    print("=" * 80)
    print(f"[PROJECT] {path.name}")
    print(f"[PATH] {path}")
    print("=" * 80 + "\n")

    print("[SUMMARY]")
    print(f"Total files scanned: {total_files}")
    print(f"Total lines (estimated): {total_lines}")
    print("File types:")
    for ext, count in file_type_counts.most_common():
        print(f"  {ext or '[no ext]'}: {count}")
    print(f"Python files: {python_file_count}")
    print(f"Total functions: {total_functions}")
    print(f"Total classes: {total_classes}")
    print(f"Unique imports ({len(imports)}): {', '.join(sorted(imports)) if imports else '(none)'}")
    print("\nTop 10 largest files by lines:")
    for f in sorted(files_detail, key=lambda x: x['lines'], reverse=True)[:10]:
        print(f"  {f['path']}: {f['lines']} lines, {f['functions']} funcs, {f['classes']} classes")

    return 0


def main():
    project_path = Path(r"C:\Users\Admin\Desktop\pdf")
    return analyze_project(project_path)


if __name__ == "__main__":
    sys.exit(main())