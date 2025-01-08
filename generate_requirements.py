import os
import re
import subprocess

def extract_imports(file_path):
    imports = set()
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Match "import" and "from" statements
            match = re.match(r'^\s*(import|from)\s+([a-zA-Z0-9_\.]+)', line)
            if match:
                module = match.group(2).split('.')[0]
                imports.add(module)
    return imports

def generate_requirements():
    py_files = [f for f in os.listdir('.') if f.endswith('.py')]
    all_imports = set()

    for py_file in py_files:
        all_imports.update(extract_imports(py_file))

    # Resolve installed packages for the found imports
    resolved_packages = set()
    for module in all_imports:
        try:
            result = subprocess.check_output(['pip', 'show', module], stderr=subprocess.DEVNULL)
            package_name = re.search(r'^Name:\s+(.+)$', result.decode('utf-8'), re.MULTILINE)
            if package_name:
                resolved_packages.add(package_name.group(1))
        except subprocess.CalledProcessError:
            # Skip if module not found in installed packages
            pass

    # Write to requirements.txt
    with open('requirements.txt', 'w') as req_file:
        for package in sorted(resolved_packages):
            req_file.write(f"{package}\n")

if __name__ == "__main__":
    generate_requirements()
