#!/usr/bin/env python3
import os
import sys
import subprocess
import tempfile
import urllib.request

def main():
    if os.environ.get('CI') or os.environ.get('POP_SKIP_INSTALL'):
        return
    
    url = "https://raw.githubusercontent.com/inference-labs-inc/proof-of-portfolio/main/install.sh"
    
    try:
        with urllib.request.urlopen(url) as response:
            script_content = response.read().decode('utf-8')
    except Exception as e:
        print(f"Failed to download install script: {e}")
        sys.exit(1)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    
    try:
        os.chmod(script_path, 0o755)
        result = subprocess.run(['/bin/bash', script_path, '--all'], 
                              capture_output=True, text=True)
        
        if result.returncode != 0:
            print("Installation failed:")
            print(result.stderr)
            sys.exit(1)
            
    except Exception as e:
        print(f"Failed to run install script: {e}")
        sys.exit(1)
    finally:
        if os.path.exists(script_path):
            os.unlink(script_path)

if __name__ == '__main__':
    main()