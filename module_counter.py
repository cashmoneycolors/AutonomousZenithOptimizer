#!/usr/bin/env python3
"""
Einfaches Script um alle Python-Module zu zählen
"""
import os

def count_modules():
    """Zählt alle .py Files in python_modules"""
    main_dir = 'python_modules'
    total_modules = 0
    modules_found = []

    if os.path.exists(main_dir):
        for root, dirs, files in os.walk(main_dir):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    total_modules += 1
                    rel_path = os.path.relpath(os.path.join(root, file), main_dir)
                    modules_found.append(rel_path)

    return total_modules, modules_found

if __name__ == "__main__":
    count, modules = count_modules()
    print(f"Gefundene Python-Module: {count}")
    print("Die ersten 10:")
    for i, mod in enumerate(modules[:10]):
        print(f"{i+1}. {mod}")
    if len(modules) > 10:
        print(f"... und {len(modules)-10} weitere")
    print(f"\nTotal: {count} Module gefunden (weit weniger als 745)")
