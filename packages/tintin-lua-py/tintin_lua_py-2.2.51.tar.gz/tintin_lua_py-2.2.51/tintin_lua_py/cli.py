#!/usr/bin/env python3
"""
TinTin++ with Lua and Python support CLI launcher
"""

import os
import sys
import subprocess
import pkg_resources
import stat


def get_tintin_binary():
    """Get the path to the bundled TinTin++ binary"""
    try:
        binary_path = pkg_resources.resource_filename('tintin_lua_py', 'bin/tt++')
        
        # Make sure binary is executable
        current_permissions = os.stat(binary_path).st_mode
        os.chmod(binary_path, current_permissions | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
        
        return binary_path
    except Exception as e:
        print(f"Error locating TinTin++ binary: {e}")
        sys.exit(1)


def main():
    """Main entry point"""
    tintin_binary = get_tintin_binary()
    
    # Set up environment
    env = os.environ.copy()
    if 'LD_LIBRARY_PATH' in env:
        env['LD_LIBRARY_PATH'] = f"/usr/local/lib:{env['LD_LIBRARY_PATH']}"
    else:
        env['LD_LIBRARY_PATH'] = "/usr/local/lib"
    
    # Build command with user arguments
    cmd = [tintin_binary] + sys.argv[1:]
    
    # Execute TinTin++
    try:
        subprocess.run(cmd, env=env)
    except KeyboardInterrupt:
        print("\nTinTin++ interrupted by user")
    except Exception as e:
        print(f"Error running TinTin++: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
