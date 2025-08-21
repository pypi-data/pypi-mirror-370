import os
import ast
import re
import subprocess
import sys


def extract_imports_from_file(file_path):
    """Extract all import statements from a Python file."""
    imports = set()

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()

        # Parse the AST
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name.split('.')[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module.split('.')[0])

    except (SyntaxError, UnicodeDecodeError, Exception) as e:
        print(f"Error parsing {file_path}: {e}")

    return imports


def get_all_python_files(directory):
    """Recursively get all Python files in directory."""
    python_files = []

    for root, dirs, files in os.walk(directory):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if
                   d not in {'.git', '__pycache__', '.venv', 'venv', 'env', 'node_modules', '.pytest_cache'}]

        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))

    return python_files


def get_installed_packages():
    """Get list of installed packages."""
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'list'],
                                capture_output=True, text=True, check=True)
        installed = {}
        lines = result.stdout.strip().split('\n')[2:]  # Skip header

        for line in lines:
            parts = line.split()
            if len(parts) >= 2:
                installed[parts[0].lower().replace('-', '_')] = parts[1]

        return installed
    except subprocess.CalledProcessError:
        print("Warning: Could not get installed packages list")
        return {}


def generate_requirements(project_dir):
    """Generate requirements.txt for the project."""

    # Built-in modules (don't need to be in requirements.txt)
    builtin_modules = {
        'os', 'sys', 'json', 'datetime', 'time', 'math', 'random', 'collections',
        'itertools', 'functools', 'operator', 're', 'string', 'io', 'pathlib',
        'typing', 'dataclasses', 'enum', 'abc', 'copy', 'pickle', 'csv', 'sqlite3',
        'urllib', 'http', 'email', 'html', 'xml', 'logging', 'threading', 'multiprocessing',
        'subprocess', 'argparse', 'configparser', 'tempfile', 'shutil', 'glob', 'fnmatch',
        'platform', 'socket', 'ssl', 'hashlib', 'base64', 'binascii', 'struct',
        'array', 'weakref', 'gc', 'inspect', 'ast', 'dis', 'importlib', 'pkgutil',
        'warnings', 'contextlib', 'unittest', 'doctest', 'pdb', 'profile', 'timeit',
        'trace', 'decimal', 'fractions', 'statistics', 'queue', 'heapq', 'bisect',
        'zlib', 'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile'
    }

    print(f"Scanning Python files in: {project_dir}")
    python_files = get_all_python_files(project_dir)
    print(f"Found {len(python_files)} Python files")

    all_imports = set()

    # Extract imports from all files
    for file_path in python_files:
        imports = extract_imports_from_file(file_path)
        all_imports.update(imports)
        print(f"Processed: {os.path.relpath(file_path, project_dir)}")

    # Filter out built-in modules
    external_imports = all_imports - builtin_modules

    # Get installed packages with versions
    installed_packages = get_installed_packages()

    # Match imports with installed packages
    requirements = []
    not_found = []

    for import_name in sorted(external_imports):
        # Common package name mappings
        package_mappings = {
            'cv2': 'opencv-python',
            'PIL': 'Pillow',
            'sklearn': 'scikit-learn',
            'yaml': 'PyYAML',
            'dotenv': 'python-dotenv',
            'jwt': 'PyJWT',
            'bs4': 'beautifulsoup4',
            'dateutil': 'python-dateutil'
        }

        package_name = package_mappings.get(import_name, import_name)
        package_key = package_name.lower().replace('-', '_')

        if package_key in installed_packages:
            requirements.append(f"{package_name}=={installed_packages[package_key]}")
        else:
            # Try original import name
            import_key = import_name.lower().replace('-', '_')
            if import_key in installed_packages:
                requirements.append(f"{import_name}=={installed_packages[import_key]}")
            else:
                not_found.append(import_name)

    # Write requirements.txt
    output_file = os.path.join(project_dir, 'requirements.txt')
    with open(output_file, 'w') as f:
        for req in sorted(requirements):
            f.write(req + '\n')

    print(f"\n✅ Generated requirements.txt with {len(requirements)} packages")
    print(f"📍 Location: {output_file}")

    if requirements:
        print("\n📦 Found packages:")
        for req in sorted(requirements):
            print(f"  {req}")

    if not_found:
        print(f"\n⚠️  Could not find version info for:")
        for pkg in sorted(not_found):
            print(f"  {pkg}")
        print("You may need to install these or add them manually")


if __name__ == "__main__":
    # Use current directory or specify your project path
    project_directory = "fincept_terminal"  # Change this to your project path

    if not os.path.exists(project_directory):
        project_directory = input("Enter your project directory path: ").strip()

    if os.path.exists(project_directory):
        generate_requirements(project_directory)
    else:
        print(f"❌ Directory '{project_directory}' not found!")