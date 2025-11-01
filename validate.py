#!/usr/bin/env python3
"""
Validation script for Azure MCP Server.
Tests the server structure and validates the implementation without requiring Azure dependencies.
"""

import ast
import sys
from pathlib import Path


def test_file_structure():
    """Test that all required files exist."""
    print("Testing file structure...")
    
    required_files = [
        "pyproject.toml",
        "README.md",
        ".gitignore",
        "src/azure_mcp/__init__.py",
        "src/azure_mcp/__main__.py",
        "src/azure_mcp/server.py",
    ]
    
    for file_path in required_files:
        path = Path(file_path)
        if not path.exists():
            print(f"  ✗ Missing required file: {file_path}")
            return False
        print(f"  ✓ Found: {file_path}")
    
    return True


def test_python_syntax():
    """Test Python files for syntax errors."""
    print("\nTesting Python syntax...")
    
    python_files = [
        "src/azure_mcp/__init__.py",
        "src/azure_mcp/__main__.py",
        "src/azure_mcp/server.py",
    ]
    
    for file_path in python_files:
        try:
            with open(file_path, 'r') as f:
                ast.parse(f.read())
            print(f"  ✓ Valid syntax: {file_path}")
        except SyntaxError as e:
            print(f"  ✗ Syntax error in {file_path}: {e}")
            return False
    
    return True


def test_package_metadata():
    """Test package metadata."""
    print("\nTesting package metadata...")
    
    # Use importlib to load module from path without modifying sys.path
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "azure_mcp",
        "src/azure_mcp/__init__.py"
    )
    if spec and spec.loader:
        azure_mcp = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(azure_mcp)
        version = azure_mcp.__version__
        print(f"  ✓ Package version: {version}")
        return True
    else:
        print("  ✗ Failed to load package")
        return False


def test_server_structure():
    """Test server implementation structure."""
    print("\nTesting server structure...")
    
    with open('src/azure_mcp/server.py', 'r') as f:
        content = f.read()
    
    # Check for required components
    checks = [
        ("AzureMcpServer class", "class AzureMcpServer"),
        ("DefaultAzureCredential import", "from azure.identity import DefaultAzureCredential"),
        ("MCP Server import", "from mcp.server.lowlevel import Server"),
        ("stdio_server import", "from mcp.server.stdio import stdio_server"),
        ("list_subscriptions tool", '"list_subscriptions"'),
        ("get_subscription_info tool", '"get_subscription_info"'),
        ("list_resource_groups tool", '"list_resource_groups"'),
        ("list_resources tool", '"list_resources"'),
        ("list_storage_accounts tool", '"list_storage_accounts"'),
        ("main entry point", "def main("),
        ("click command decorator", "@click.command()"),
    ]
    
    all_passed = True
    for name, check_str in checks:
        if check_str in content:
            print(f"  ✓ Found: {name}")
        else:
            print(f"  ✗ Missing: {name}")
            all_passed = False
    
    return all_passed


def test_entrypoint():
    """Test entry point configuration."""
    print("\nTesting entry point...")
    
    with open('pyproject.toml', 'r') as f:
        content = f.read()
    
    if 'azure-mcp = "azure_mcp.server:main"' in content:
        print("  ✓ Entry point configured correctly")
        return True
    else:
        print("  ✗ Entry point not found in pyproject.toml")
        return False


def test_readme():
    """Test README documentation."""
    print("\nTesting README documentation...")
    
    with open('README.md', 'r') as f:
        content = f.read()
    
    checks = [
        ("Installation section", "## Installation"),
        ("Usage section", "## Usage"),
        ("Authentication section", "## Authentication"),
        ("Tools documentation", "### 1. `list_subscriptions`"),
        ("MCP configuration", "## MCP Configuration"),
        ("python -m azure_mcp.server command", "python -m azure_mcp.server"),
    ]
    
    all_passed = True
    for name, check_str in checks:
        if check_str in content:
            print(f"  ✓ Found: {name}")
        else:
            print(f"  ✗ Missing: {name}")
            all_passed = False
    
    return all_passed


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("Azure MCP Python Server - Validation Tests")
    print("=" * 60)
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_package_metadata,
        test_server_structure,
        test_entrypoint,
        test_readme,
    ]
    
    results = []
    for test in tests:
        try:
            results.append(test())
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            results.append(False)
    
    print("\n" + "=" * 60)
    print("Test Results")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nPassed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All validation tests passed!")
        return 0
    else:
        print("\n✗ Some validation tests failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
