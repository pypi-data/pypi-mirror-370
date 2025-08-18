import subprocess
import sys
import os

def install_python_requirements(project_path):
    print("Installing Python dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", os.path.join(project_path, "requirements.txt")])

def install_npm_dependencies(project_path):
    print("Installing Tailwind CSS via npm...")
    subprocess.run(["npm", "install"], cwd=project_path)
