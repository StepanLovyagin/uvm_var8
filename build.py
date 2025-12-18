import os
import shutil
import subprocess
import platform
import sys

DIST = "dist"
FILES = ["index.html", "assembler.py", "interpreter.py"]

def main():
    if os.path.exists(DIST): shutil.rmtree(DIST)
    
    #build web
    web_dir = os.path.join(DIST, "web")
    os.makedirs(web_dir)
    for f in FILES: 
        if os.path.exists(f):
            shutil.copy(f, os.path.join(web_dir, f))
    print(f"Web build: {web_dir}")

    #build desktop
    os_name = platform.system()
    exe_name = f"UVM_App_{os_name}"
    desktop_dir = os.path.join(DIST, "desktop")
    print(f"Building Desktop для {os_name}...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller", "--noconsole", "--onefile", 
            "--name", exe_name,
            "--distpath", desktop_dir,
            "uvm_gui.py"
        ], check=True)
        
        if os.path.exists("vector_mul_5x6.csv"):
            shutil.copy("vector_mul_5x6.csv", os.path.join(desktop_dir, "vector_mul_5x6.csv"))
            
        print(f"Desktop build успешен!")
    except Exception as e:
        print(f"Desktop build провален (PyInstaller missing?): {e}")

if __name__ == "__main__":
    main()