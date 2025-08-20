import os
import shutil
from pathlib import Path
from setuptools import setup, Extension, find_namespace_packages
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.sdist import sdist as _sdist
from setuptools.command.build_ext import build_ext as _build_ext
from Cython.Build import cythonize

# Configuration
PACKAGE_NAME = "matrice_data_processing"
VERSION = "0.1.1"
SOURCE_DIR = f"src/{PACKAGE_NAME}"
STAGING_DIR = f"{PACKAGE_NAME}_compiled/{PACKAGE_NAME}"
BUILD_DIR = "build"

class CustomBuildExt(_build_ext):
    """Custom build_ext for Cython compilation and staging."""
    def run(self):
        try:
            _build_ext.run(self)
            os.makedirs(STAGING_DIR, exist_ok=True)

            # Copy .so files to staging directory
            so_files = []
            build_package_dir = os.path.join(self.build_lib, PACKAGE_NAME)
            for root, _, files in os.walk(build_package_dir):
                for file in files:
                    if file.endswith(".so"):
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, build_package_dir)
                        dest_path = os.path.join(STAGING_DIR, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(src_path, dest_path)
                        so_files.append(dest_path)

            # Copy __init__.py, __init__.pyi, py.typed, and other .pyi files
            for file in ["__init__.py", "__init__.pyi", "py.typed"]:
                src_path = os.path.join(SOURCE_DIR, file)
                if os.path.exists(src_path):
                    dest_path = os.path.join(STAGING_DIR, file)
                    shutil.copy2(src_path, dest_path)

            for pyi_file in Path(SOURCE_DIR).rglob("*.pyi"):
                if pyi_file.name != "__init__.pyi":
                    rel_path = os.path.relpath(pyi_file, SOURCE_DIR)
                    dest_path = os.path.join(STAGING_DIR, rel_path)
                    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                    shutil.copy2(pyi_file, dest_path)

            if not so_files:
                print("Warning: No .so files were compiled. Check Cython compilation.")
            else:
                print(f"Compiled and staged {len(so_files)} .so files: {so_files}")
        except Exception as e:
            print(f"Error in CustomBuildExt: {e}")
            raise

class CustomBuildPy(_build_py):
    """Custom build_py to copy files from staging directory to build/lib."""
    def run(self):
        try:
            self.run_command("build_ext")
            build_package_dir = os.path.join(self.build_lib, PACKAGE_NAME)
            os.makedirs(build_package_dir, exist_ok=True)
            for root, _, files in os.walk(STAGING_DIR):
                for file in files:
                    if file.endswith((".so", ".pyi", "py.typed", "__init__.py")):
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, STAGING_DIR)
                        dest_path = os.path.join(build_package_dir, rel_path)
                        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                        shutil.copy2(src_path, dest_path)
        except Exception as e:
            print(f"Error in CustomBuildPy: {e}")
            raise

    def find_package_modules(self, package, package_dir):
        modules = []
        staging_package_dir = os.path.join(STAGING_DIR)
        if os.path.exists(staging_package_dir):
            for file in Path(staging_package_dir).rglob("*"):
                if file.suffix == ".so":
                    module_name = file.stem.split(".")[0]
                    rel_path = os.path.relpath(file, staging_package_dir)
                    module_path = os.path.join(PACKAGE_NAME, rel_path)
                    modules.append((PACKAGE_NAME, module_name, module_path))
        return modules

class CustomSdist(_sdist):
    """Custom sdist to include specific files from staging directory."""
    def run(self):
        try:
            self.run_command("build_ext")
            super().run()
        except Exception as e:
            print(f"Error in CustomSdist: {e}")
            raise

    def get_file_list(self):
        self.filelist.files = [
            os.path.join(STAGING_DIR, "__init__.py"),
            os.path.join(STAGING_DIR, "__init__.pyi"),
            os.path.join(STAGING_DIR, "py.typed"),
            "README.md",
            "LICENSE.txt",
            "pyproject.toml",
            "setup.py",
        ] + [str(f) for f in Path(STAGING_DIR).rglob("*.so")] + [
            str(f) for f in Path(STAGING_DIR).rglob("*.pyi") if f.name != "__init__.pyi"
        ]
        self.filelist.files = [f for f in self.filelist.files if os.path.exists(f)]

def find_python_files(source_dir):
    """Find Python files to compile, excluding specific files."""
    exclude_files = ["__init__.py"]
    python_files = []
    source_path = Path(source_dir)
    if not source_path.exists():
        print(f"Directory {source_dir} not found!")
        return []
    for py_file in source_path.rglob("*.py"):
        if py_file.name not in exclude_files:
            python_files.append(str(py_file))
    return python_files

def create_extensions(source_dir):
    """Create Cython extensions from .py files."""
    python_files = find_python_files(source_dir)
    if not python_files:
        print("No Python files found to compile!")
        return []
    extensions = []
    for py_file in python_files:
        rel_path = os.path.relpath(py_file, source_dir)
        module_name = rel_path.replace(os.sep, '.')[:-3]
        extensions.append(Extension(
            name=f"{PACKAGE_NAME}.{module_name}",
            sources=[py_file],
            extra_compile_args=["-O3"],
        ))
    return extensions

# Create py.typed file if it doesn't exist
py_typed_path = os.path.join(STAGING_DIR, "py.typed")
if not os.path.exists(py_typed_path):
    os.makedirs(STAGING_DIR, exist_ok=True)
    with open(py_typed_path, "w") as f:
        f.write("")
elif not os.path.exists(os.path.join(SOURCE_DIR, "py.typed")):
    src_py_typed = os.path.join(SOURCE_DIR, "py.typed")
    if os.path.exists(src_py_typed):
        shutil.copy2(src_py_typed, py_typed_path)

setup(
    name=PACKAGE_NAME,
    version="0.1.3",
    packages=[PACKAGE_NAME],
    package_dir={PACKAGE_NAME: STAGING_DIR},
    include_package_data=True,
    package_data={
        PACKAGE_NAME: [
            "*.so",
            "*.pyi",
            "py.typed",
            "__init__.py",
            "**/*.so",
            "**/*.pyi",
            "**/py.typed",
            "**/__init__.py",
        ],
    },
    ext_modules=cythonize(
        create_extensions(SOURCE_DIR),
        build_dir=BUILD_DIR,
        compiler_directives={
            'language_level': 3,
            'boundscheck': False,
            'wraparound': False,
            'cdivision': True,
            'embedsignature': True,
            'optimize.use_switch': True,
        },
        annotate=False,
    ),
    cmdclass={
        'build_ext': CustomBuildExt,
        'build_py': CustomBuildPy,
        'sdist': CustomSdist,
    },
    zip_safe=False,
    options={
        "bdist_wheel": {
            "universal": False,
            "plat_name": "manylinux_2_17_x86_64"
        }
    }
)