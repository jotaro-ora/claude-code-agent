#!/usr/bin/env python3
"""
Simple CLI Verification Script

This script verifies that all tools have CLI functionality by checking for the presence
of argparse imports and if __name__ == "__main__" blocks.
"""

import os
import re
from pathlib import Path

def check_cli_functionality():
    """Check CLI functionality for all tools."""
    tools_dir = Path(__file__).parent.parent  # Go up one level to /tools/
    tools = []
    
    # Find all Python files in tools directory (including subdirectories)
    for file_path in tools_dir.glob("*.py"):
        if file_path.name.startswith("__") or file_path.name in ["README.md", "tools_list.md"]:
            continue
        tools.append(file_path)
    
    # Find Python files in CoinGlass directory
    coinglass_dir = tools_dir / "coinglass"
    if coinglass_dir.exists():
        for file_path in coinglass_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            tools.append(file_path)
    
    # Find Python files in LunaCrush directory
    lunacrush_dir = tools_dir / "lunacrush"
    if lunacrush_dir.exists():
        for file_path in lunacrush_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue
            tools.append(file_path)
    
    print("Checking CLI functionality for all tools...")
    print("=" * 60)
    
    results = []
    
    for tool_path in sorted(tools):
        # Get relative path from tools directory
        rel_path = tool_path.relative_to(tools_dir)
        print(f"Checking {rel_path}...")
        
        try:
            with open(tool_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for argparse import
            has_argparse = 'import argparse' in content or 'from argparse import' in content
            
            # Check for if __name__ == "__main__" block
            has_main_block = 'if __name__ == "__main__":' in content
            
            # Check for argument parser creation
            has_parser = 'argparse.ArgumentParser' in content
            
            # Check for parse_args call
            has_parse_args = 'parse_args()' in content
            
            # Check for help text
            has_help = 'help=' in content
            
            # Check for output format support
            has_output_format = 'output_format' in content
            
            status = "✅" if all([has_argparse, has_main_block, has_parser, has_parse_args]) else "❌"
            
            result = {
                'tool': str(rel_path),
                'status': status,
                'has_argparse': has_argparse,
                'has_main_block': has_main_block,
                'has_parser': has_parser,
                'has_parse_args': has_parse_args,
                'has_help': has_help,
                'has_output_format': has_output_format
            }
            
            results.append(result)
            
            print(f"  {status} CLI functionality")
            if not all([has_argparse, has_main_block, has_parser, has_parse_args]):
                print(f"    Missing: ", end="")
                missing = []
                if not has_argparse:
                    missing.append("argparse import")
                if not has_main_block:
                    missing.append("main block")
                if not has_parser:
                    missing.append("argument parser")
                if not has_parse_args:
                    missing.append("parse_args call")
                print(", ".join(missing))
            
        except Exception as e:
            print(f"  ❌ Error reading file: {e}")
            results.append({
                'tool': str(rel_path),
                'status': "❌",
                'error': str(e)
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    total_tools = len(results)
    working_tools = sum(1 for r in results if r['status'] == "✅")
    
    print(f"Total tools: {total_tools}")
    print(f"Working CLI: {working_tools}")
    print(f"Missing CLI: {total_tools - working_tools}")
    print(f"Success rate: {(working_tools/total_tools)*100:.1f}%")
    
    if working_tools == total_tools:
        print("\n🎉 All tools have CLI functionality!")
    else:
        print(f"\n⚠️  {total_tools - working_tools} tool(s) missing CLI functionality")
    
    # Show detailed results
    print("\nDetailed Results:")
    print("-" * 60)
    for result in results:
        if result['status'] == "✅":
            features = []
            if result.get('has_help'):
                features.append("help text")
            if result.get('has_output_format'):
                features.append("output format")
            features_str = f" ({', '.join(features)})" if features else ""
            print(f"✅ {result['tool']}{features_str}")
        else:
            print(f"❌ {result['tool']}")
            if 'error' in result:
                print(f"    Error: {result['error']}")

if __name__ == "__main__":
    check_cli_functionality() 