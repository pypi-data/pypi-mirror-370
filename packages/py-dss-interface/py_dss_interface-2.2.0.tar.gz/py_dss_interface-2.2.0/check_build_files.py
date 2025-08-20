#!/usr/bin/env python3
"""
Script to check what files are being included in the build
"""

import os
import sys
from pathlib import Path

def check_manifest_inclusion():
    """Check what files would be included based on MANIFEST.in"""
    print("=== Checking MANIFEST.in inclusion ===\n")
    
    # Read MANIFEST.in
    manifest_path = Path("MANIFEST.in")
    if not manifest_path.exists():
        print("❌ MANIFEST.in not found!")
        return
    
    with open(manifest_path, 'r') as f:
        manifest_content = f.read()
    
    print("MANIFEST.in content:")
    print(manifest_content)
    print("\n" + "="*50 + "\n")

def check_pyproject_inclusion():
    """Check what files would be included based on pyproject.toml"""
    print("=== Checking pyproject.toml inclusion ===\n")
    
    # Read pyproject.toml
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("❌ pyproject.toml not found!")
        return
    
    with open(pyproject_path, 'r') as f:
        pyproject_content = f.read()
    
    # Extract package-data section
    lines = pyproject_content.split('\n')
    in_package_data = False
    package_data_lines = []
    
    for line in lines:
        if '[tool.setuptools.package-data]' in line:
            in_package_data = True
            package_data_lines.append(line)
        elif in_package_data:
            if line.strip().startswith('[') and line.strip().endswith(']'):
                break
            package_data_lines.append(line)
    
    print("Package data configuration:")
    for line in package_data_lines:
        print(line)
    print("\n" + "="*50 + "\n")

def check_actual_files():
    """Check if the actual files exist"""
    print("=== Checking actual files ===\n")
    
    google_colab_dir = Path("src/py_dss_interface/opendss_official/linux/google_colab")
    
    if not google_colab_dir.exists():
        print(f"❌ Directory not found: {google_colab_dir}")
        return
    
    print(f"✅ Directory exists: {google_colab_dir}")
    
    expected_files = [
        "libOpenDSSC.so",
        "libklusolve_all.so",
        "libklusolve_all.so.0",
        "libklusolve_all.so.0.0.0",
        "versions.txt"
    ]
    
    for file_name in expected_files:
        file_path = google_colab_dir / file_name
        if file_path.exists():
            size = file_path.stat().st_size
            print(f"✅ {file_name} exists ({size:,} bytes)")
        else:
            print(f"❌ {file_name} missing")
    
    print("\n" + "="*50 + "\n")

def simulate_build_inclusion():
    """Simulate what files would be included in the build"""
    print("=== Simulating build inclusion ===\n")
    
    # This is a simplified simulation
    google_colab_dir = Path("src/py_dss_interface/opendss_official/linux/google_colab")
    
    if not google_colab_dir.exists():
        print("❌ Google Colab directory not found!")
        return
    
    # Check if the directory would be included
    print("Based on MANIFEST.in patterns:")
    print("- recursive-include src/py_dss_interface/opendss_official/linux/google_colab/ *.so")
    print("- recursive-include src/py_dss_interface/opendss_official/linux/google_colab/ *.txt")
    print("- explicit includes for each file")
    
    print("\nBased on pyproject.toml patterns:")
    print("- opendss_official/**/* (should include everything)")
    print("- explicit patterns for google_colab files")
    
    print("\nExpected result: All Google Colab files should be included")
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("🔍 BUILD FILE INCLUSION CHECKER\n")
    
    check_actual_files()
    check_manifest_inclusion()
    check_pyproject_inclusion()
    simulate_build_inclusion()
    
    print("💡 RECOMMENDATIONS:")
    print("1. Make sure you're using 'py -m build' or 'python -m build'")
    print("2. Check the dist/ directory after building")
    print("3. Extract the wheel file and verify the files are inside")
    print("4. If files are still missing, try using setuptools directly")
