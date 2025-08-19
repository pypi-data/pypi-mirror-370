#!/usr/bin/env python3
"""
LumeTT CLI launcher
"""

import os
import sys
import shutil
import subprocess
import pkg_resources
from pathlib import Path


def setup_config():
    """Set up user configuration directory"""
    config_dir = Path.home() / '.lumett'
    
    if not config_dir.exists():
        print("First run detected. Setting up Lumett configuration...")
        config_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy data files from package
        try:
            data_path = pkg_resources.resource_filename('lumett', 'data')
            shutil.copytree(data_path, config_dir, dirs_exist_ok=True)
            
            # Make files writable
            for root, dirs, files in os.walk(config_dir):
                for name in files:
                    filepath = os.path.join(root, name)
                    os.chmod(filepath, 0o644)
                for name in dirs:
                    dirpath = os.path.join(root, name)
                    os.chmod(dirpath, 0o755)
                    
        except Exception as e:
            print(f"Error setting up configuration: {e}")
            sys.exit(1)
    
    return config_dir


def find_tintin():
    """Find TinTin++ executable"""
    # First try to find tintin-lua-py (enhanced version)
    enhanced_candidates = ['tintin-lua-py', 'tt++']
    
    for candidate in enhanced_candidates:
        if shutil.which(candidate):
            print(f"Using enhanced TinTin++ from: {candidate}")
            return candidate
    
    # Fall back to standard TinTin++ versions
    standard_candidates = ['tintin++', 'tintin']
    
    for candidate in standard_candidates:
        if shutil.which(candidate):
            print(f"Using standard TinTin++: {candidate}")
            print("Note: For enhanced Lua/Python support, install tintin-lua-py package")
            return candidate
    
    print("Error: TinTin++ not found in PATH")
    print("Please install TinTin++ first:")
    print("  pip install tintin-lua-py  (recommended - enhanced version)")
    print("  or")
    print("  sudo apt install tintin++  (standard version)")
    sys.exit(1)


def main():
    """Main entry point"""
    config_dir = setup_config()
    tintin_exe = find_tintin()
    
    # Set environment
    env = os.environ.copy()
    if 'LD_LIBRARY_PATH' in env:
        env['LD_LIBRARY_PATH'] = f"/usr/local/lib:{env['LD_LIBRARY_PATH']}"
    else:
        env['LD_LIBRARY_PATH'] = "/usr/local/lib"
    
    # Change to config directory
    os.chdir(config_dir)
    
    # Build command
    init_file = config_dir / 'lib' / 'init.tin'
    cmd = [tintin_exe, '-t', 'LumeTT Client']
    
    if init_file.exists():
        cmd.extend(['-r', str(init_file)])
    
    # Add user arguments
    cmd.extend(sys.argv[1:])
    
    # Execute TinTin++
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nLumeTT interrupted by user")
    except Exception as e:
        print(f"Error running LumeTT: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
