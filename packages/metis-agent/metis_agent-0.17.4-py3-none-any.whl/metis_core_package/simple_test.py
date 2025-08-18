#!/usr/bin/env python3
"""Simple test of refactored components."""

import sys
import os
from pathlib import Path

def test_files():
    """Test if refactored files exist."""
    print("Testing refactored files...")
    
    files = [
        "metis_agent/cli/refactored/command_router.py",
        "metis_agent/cli/refactored/streaming/core.py", 
        "metis_agent/core/refactored/orchestrator/core.py"
    ]
    
    results = []
    for file_path in files:
        exists = os.path.exists(file_path)
        print(f"{file_path}: {'EXISTS' if exists else 'MISSING'}")
        results.append(exists)
    
    return all(results)

def test_tool_registry():
    """Test tool registry."""
    print("\nTesting tool registry...")
    
    # Add metis_agent to path
    sys.path.insert(0, str(Path(__file__).parent / "metis_agent"))
    
    try:
        from tools.registry import get_available_tools
        tools = get_available_tools()
        print(f"Tools available: {len(tools)}")
        print("Some tools:", list(tools.keys())[:5])
        return True
    except Exception as e:
        print(f"Tool registry failed: {e}")
        return False

if __name__ == "__main__":
    print("TESTING REFACTORED COMPONENTS")
    print("=" * 40)
    
    files_ok = test_files()
    tools_ok = test_tool_registry()
    
    print("\n" + "=" * 40)
    print(f"Files test: {'PASS' if files_ok else 'FAIL'}")
    print(f"Tools test: {'PASS' if tools_ok else 'FAIL'}")
    print(f"Overall: {'PASS' if files_ok and tools_ok else 'FAIL'}")
