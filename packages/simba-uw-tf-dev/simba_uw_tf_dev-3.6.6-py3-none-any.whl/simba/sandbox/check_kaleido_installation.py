import os
import sys
import subprocess

def check_kaleido_installation():
    """Check what's actually installed in Kaleido paths"""
    
    print("=== Kaleido Installation Check ===\n")
    
    # Check conda environment path
    conda_env_path = sys.prefix
    print(f"Conda environment: {conda_env_path}")
    
    # Check if kaleido package is installed
    try:
        import kaleido
        print(f"✅ Kaleido package found at: {kaleido.__file__}")
    except ImportError:
        print("❌ Kaleido package not found")
        return
    
    # Check kaleido directory structure
    kaleido_dir = os.path.dirname(kaleido.__file__)
    print(f"Kaleido directory: {kaleido_dir}")
    
    # List contents of kaleido directory
    print(f"\nContents of {kaleido_dir}:")
    try:
        for item in os.listdir(kaleido_dir):
            item_path = os.path.join(kaleido_dir, item)
            if os.path.isdir(item_path):
                print(f"  📁 {item}/")
                # List contents of subdirectories
                try:
                    for subitem in os.listdir(item_path):
                        print(f"    - {subitem}")
                except:
                    print(f"    - (cannot read)")
            else:
                print(f"  📄 {item}")
    except Exception as e:
        print(f"  Error reading directory: {e}")
    
    # Check for executable directory
    executable_dir = os.path.join(kaleido_dir, "executable")
    print(f"\nExecutable directory: {executable_dir}")
    if os.path.exists(executable_dir):
        print("✅ Executable directory exists")
        try:
            for item in os.listdir(executable_dir):
                item_path = os.path.join(executable_dir, item)
                if os.path.isfile(item_path):
                    print(f"  📄 {item}")
                else:
                    print(f"  📁 {item}/")
        except Exception as e:
            print(f"  Error reading executable directory: {e}")
    else:
        print("❌ Executable directory does not exist")
    
    # Check for kaleido executable specifically
    kaleido_exe = os.path.join(executable_dir, "kaleido")
    print(f"\nKaleido executable: {kaleido_exe}")
    if os.path.exists(kaleido_exe):
        print("✅ Kaleido executable found")
        # Check if it's executable
        if os.access(kaleido_exe, os.X_OK):
            print("✅ Kaleido executable is executable")
        else:
            print("❌ Kaleido executable is not executable")
    else:
        print("❌ Kaleido executable not found")
    
    # Check system Python kaleido
    system_kaleido = r"C:\Users\sroni\AppData\Roaming\Python\Python36\site-packages\kaleido"
    print(f"\nSystem Python kaleido: {system_kaleido}")
    if os.path.exists(system_kaleido):
        print("✅ System Python kaleido exists")
        system_exe = os.path.join(system_kaleido, "executable", "kaleido")
        if os.path.exists(system_exe):
            print("✅ System Python kaleido executable exists")
        else:
            print("❌ System Python kaleido executable not found")
    else:
        print("❌ System Python kaleido does not exist")
    
    # Try to find kaleido in PATH
    print(f"\nChecking PATH for kaleido:")
    try:
        result = subprocess.run(['where', 'kaleido'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Kaleido found in PATH:")
            for line in result.stdout.strip().split('\n'):
                print(f"  {line}")
        else:
            print("❌ Kaleido not found in PATH")
    except Exception as e:
        print(f"Error checking PATH: {e}")

if __name__ == "__main__":
    check_kaleido_installation() 