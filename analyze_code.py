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


def main():
    # Get path from command line or use current directory
    if len(sys.argv) >= 2:
        project_path = Path(sys.argv[1])
    else:
        # If no argument, analyze the directory where the script is located
        project_path = Path(__file__).parent
        print(f"[INFO] No path provided, analyzing script directory: {project_path}")
    
    if not project_path.exists():
        print(f"[ERROR] Path does not exist: {project_path}")
        return 1
    
    if not project_path.is_dir():
        print(f"[ERROR] Path is not a directory: {project_path}")
        return 1
    
    print("\n" + "="*80)
    print("[CODEBASE ANALYSIS]")
    print("="*80)
    print(f"[PROJECT] {project_path.name}")
    print(f"[PATH] {project_path}")
    print("="*80 + "\n")
    
    stats = {
        'total_files': 0,
        'code_files': defaultdict(int),
        'total_lines': 0,
        'functions': defaultdict(list),
        'classes': defaultdict(list),
        'imports': set(),
        'files_detail': [],
        'file_types': defaultdict(int)
    }
    
    skip_dirs = {'.git', '__pycache__', '.env', 'venv', 'node_modules', 
                 '.pytest_cache', 'uploads', 'dist', 'build'}
    
    for root, dirs, files in os.walk(project_path):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = Path(root) / file
            rel_path = file_path.relative_to(project_path)
            stats['total_files'] += 1
            ext = file_path.suffix.lower()
            stats['file_types'][ext] += 1
            
            if ext == '.py':
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        lines = content.split('\n')
                        stats['total_lines'] += len(lines)
                    
                    tree = ast.parse(content)
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    
                    for func in functions:
                        stats['functions'][str(rel_path)].append(func)
                    for cls in classes:
                        stats['classes'][str(rel_path)].append(cls)
                    
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for alias in node.names:
                                stats['imports'].add(alias.name.split('.')[0])
                        elif isinstance(node, ast.ImportFrom):
                            if node.module:
                                stats['imports'].add(node.module.split('.')[0])
                    
                    stats['code_files']['Python'] += 1
                    stats['files_detail'].append({
                        'path': str(rel_path),
                        'language': 'Python',
                        'lines': len(lines),
                        'functions': len(functions),
                        'classes': len(classes)
                    })
                except:
                    pass
    
    # Print results
    print("[SUMMARY]")
    print("-" * 80)
    print(f"  Total Files:          {stats['total_files']}")
    print(f"  Total Lines:          {stats['total_lines']}")
    print(f"  Total Functions:      {sum(len(v) for v in stats['functions'].values())}")
    print(f"  Total Classes:        {sum(len(v) for v in stats['classes'].values())}")
    
    if stats['code_files']:
        print("\n[LANGUAGES]")
        print("-" * 80)
        for lang, count in sorted(stats['code_files'].items(), key=lambda x: x[1], reverse=True):
            print(f"  {lang:20} {count:5} files")
    
    if stats['file_types']:
        print("\n[FILE TYPES]")
        print("-" * 80)
        for ext, count in sorted(stats['file_types'].items(), key=lambda x: x[1], reverse=True):
            if ext:
                print(f"  {ext:15} {count:5} files")
    
    if stats['imports']:
        print("\n[DEPENDENCIES]")
        print("-" * 80)
        external_deps = [d for d in sorted(stats['imports']) 
                       if d not in ['os', 'sys', 'json', 'pathlib', 'collections', 'ast', 'asyncio', 're']]
        for dep in external_deps[:20]:
            print(f"  {dep}")
    
    if stats['files_detail']:
        print("\n[FILES]")
        print("-" * 80)
        for file_info in sorted(stats['files_detail'], key=lambda x: x['path']):
            print(f"\n  {file_info['path']}")
            print(f"    Language: {file_info['language']} | Lines: {file_info['lines']} | Functions: {file_info['functions']} | Classes: {file_info['classes']}")
    
    print("\n[STATISTICS]")
    print("-" * 80)
    if stats['total_files'] > 0:
        print(f"  Average lines per file: {stats['total_lines'] // stats['total_files']}")
    if stats['files_detail']:
        largest = max(stats['files_detail'], key=lambda x: x['lines'])
        print(f"  Largest file: {largest['path']} ({largest['lines']} lines)")
    
    print("\n" + "="*80)
    print("[OK] Analysis Complete!")
    print("="*80 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
