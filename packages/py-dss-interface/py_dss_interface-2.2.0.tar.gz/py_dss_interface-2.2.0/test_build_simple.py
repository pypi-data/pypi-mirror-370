#!/usr/bin/env python3
"""
Simple test to verify build process
"""

import os
import sys
from pathlib import Path

def test_file_paths():
    """Test if the file paths are correct for the build process"""
    
    print("=== Testing File Paths ===\n")
    
    # Test the exact paths that the build process would look for
    test_paths = [
        "src/py_dss_interface/opendss_official/linux/google_colab/libOpenDSSC.so",
        "src/py_dss_interface/opendss_official/linux/google_colab/libklusolve_all.so",
        "src/py_dss_interface/opendss_official/linux/google_colab/libklusolve_all.so.0",
        "src/py_dss_interface/opendss_official/linux/google_colab/libklusolve_all.so.0.0.0",
        "src/py_dss_interface/opendss_official/linux/google_colab/versions.txt"
    ]
    
    for path in test_paths:
        if Path(path).exists():
            size = Path(path).stat().st_size
            print(f"✅ {path} exists ({size:,} bytes)")
        else:
            print(f"❌ {path} missing")
    
    print("\n" + "="*50 + "\n")

def test_manifest_patterns():
    """Test if the MANIFEST.in patterns would match"""
    
    print("=== Testing MANIFEST.in Patterns ===\n")
    
    # Test the recursive-include patterns
    google_colab_dir = Path("src/py_dss_interface/opendss_official/linux/google_colab")
    
    if google_colab_dir.exists():
        # Test *.so pattern
        so_files = list(google_colab_dir.glob("*.so"))
        print(f"Files matching *.so: {len(so_files)}")
        for file in so_files:
            print(f"  - {file.name}")
        
        # Test *.txt pattern
        txt_files = list(google_colab_dir.glob("*.txt"))
        print(f"Files matching *.txt: {len(txt_files)}")
        for file in txt_files:
            print(f"  - {file.name}")
    else:
        print("❌ Google Colab directory not found")
    
    print("\n" + "="*50 + "\n")

def test_pyproject_patterns():
    """Test if the pyproject.toml patterns would match"""
    
    print("=== Testing pyproject.toml Patterns ===\n")
    
    # Test the opendss_official/**/* pattern
    opendss_dir = Path("src/py_dss_interface/opendss_official")
    
    if opendss_dir.exists():
        all_files = list(opendss_dir.rglob("*"))
        google_colab_files = [f for f in all_files if "google_colab" in str(f) and f.is_file()]
        
        print(f"All files in opendss_official: {len(all_files)}")
        print(f"Google Colab files: {len(google_colab_files)}")
        
        for file in google_colab_files:
            print(f"  - {file.relative_to(opendss_dir)}")
    else:
        print("❌ opendss_official directory not found")
    
    print("\n" + "="*50 + "\n")

if __name__ == "__main__":
    print("🔍 BUILD PATH TESTER\n")
    
    test_file_paths()
    test_manifest_patterns()
    test_pyproject_patterns()
    
    print("💡 NEXT STEPS:")
    print("1. Try building again with: py -m build")
    print("2. Check if the warnings are gone")
    print("3. Verify the files are in the built package")
