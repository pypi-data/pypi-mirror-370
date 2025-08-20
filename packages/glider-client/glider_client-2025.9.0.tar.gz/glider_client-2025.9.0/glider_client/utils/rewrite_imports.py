# -*- coding: utf-8 -*-
"""
Created by chiesa

Copyright Alpes Lasers SA, Switzerland
"""
__author__ = 'chiesa'
__copyright__ = "Copyright Alpes Lasers SA"

import os
import re

def rewrite_imports(base_dir):
    pattern = re.compile(r'from\s+glider\.client|import\s+glider\.client')
    replacement = lambda line: line.replace('glider.client', 'glider_client')

    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

                new_lines = [replacement(line) if pattern.search(line) else line for line in lines]

                if lines != new_lines:
                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    print(f"Updated: {path}")

if __name__ == "__main__":
    rewrite_imports("..")
