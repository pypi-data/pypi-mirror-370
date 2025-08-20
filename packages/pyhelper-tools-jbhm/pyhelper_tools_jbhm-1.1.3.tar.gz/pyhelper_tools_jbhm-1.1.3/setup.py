from setuptools import setup, find_packages
import os
import ast
import sys
import importlib.util

with open('README.md', 'r', encoding='utf-8') as f:
    long_description = f.read()

def find_imports_in_file(filepath):
    """
    Parses a Python file and extracts top-level imported packages.
    Returns a set of base package names.
    """
    with open(filepath, "r", encoding="utf-8") as file:
        node = ast.parse(file.read(), filename=filepath)

    imports = set()
    for n in ast.walk(node):
        if isinstance(n, ast.Import):
            for alias in n.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(n, ast.ImportFrom):
            if n.module:
                imports.add(n.module.split(".")[0])
    return imports

def collect_all_imports(target_dir="helper"):
    """
    Walks through all .py files in the target directory and its subdirs,
    collecting all unique imported modules.
    """
    all_imports = set()
    for root, _, files in os.walk(target_dir):
        for file in files:
            if file.endswith(".py"):
                path = os.path.join(root, file)
                all_imports.update(find_imports_in_file(path))
    return sorted(all_imports)

# Packages you know are needed from PyPI (standard lib ones serán ignorados por pip)
raw_deps = collect_all_imports()
internal_modules = {"core", "submodules", "helper"}

# Hardcoded whitelist of standard library modules to ignore (Python >=3.8)
def is_stdlib(module_name):
    spec = importlib.util.find_spec(module_name)
    return spec is not None and 'site-packages' not in (spec.origin or '')


# Only include external dependencies
install_requires = [pkg for pkg in raw_deps if not is_stdlib(pkg) and pkg not in internal_modules]

setup(
    name="pyhelper-tools-jbhm",
    version="1.1.3",
    description="A centralized data-handling toolkit for Python developers",
    author="Juan Braian Hernandez Morani",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    package_data={"helper": ["translations.json"]},
    include_package_data=True,
    install_requires=install_requires,
    python_requires=">=3.8"
)