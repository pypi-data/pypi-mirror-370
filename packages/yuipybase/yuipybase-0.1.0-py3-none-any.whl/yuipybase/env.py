import subprocess
import sys
import os

def create_virtualenv(env_name="venv"):
    if not os.path.exists(env_name):
        subprocess.check_call([sys.executable, "-m", "venv", env_name])
        print(f"Created virtual environment: {env_name}")
    else:
        print(f"Virtual environment '{env_name}' already exists.")

def install_packages(env_name="venv", packages=None):
    if packages is None:
        packages = ["numpy", "pandas", "requests"]
    pip_path = os.path.join(env_name, "Scripts", "pip") if os.name == "nt" else os.path.join(env_name, "bin", "pip")
    subprocess.check_call([pip_path, "install"] + packages)
    print(f"Installed packages: {packages}")
