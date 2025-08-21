from setuptools import setup, find_packages
import os
import shutil

# Read README for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Copy submodule content into package before building
def copy_icon_files():
    """Copy icon files from submodules into the package."""
    icon_sources = [
        ('submodules/simple-icons/icons', 'resumate/icons/simple-icons'),
        ('submodules/fontawesome/svgs', 'resumate/icons/fontawesome'),
    ]
    
    for src, dst in icon_sources:
        if os.path.exists(src):
            os.makedirs(dst, exist_ok=True)
            # Copy SVG files
            for root, dirs, files in os.walk(src):
                for file in files:
                    if file.endswith('.svg'):
                        src_file = os.path.join(root, file)
                        # Maintain directory structure
                        rel_path = os.path.relpath(src_file, src)
                        dst_file = os.path.join(dst, rel_path)
                        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
                        shutil.copy2(src_file, dst_file)

copy_icon_files()

setup(
    name='resumate',
    version='0.1.3',  # Bump version for the fix
    author='Charles Watkins',
    author_email='chris@watkinslabs.com',
    description='Beautiful PDF resumes from YAML - for humans, not ATS',
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url='https://github.com/chris17453/resumate/',
    project_urls={
        "Bug Tracker": "https://github.com/chris17453/resumate/issues",
        "Documentation": "https://github.com/chris17453/resumate",
        "Source Code": "https://github.com/chris17453/resumate",
    },
    
    # Python version requirement - support 3.7+
    python_requires='>=3.7',
    
    packages=find_packages(),
    package_data={
        'resumate': [
            'templates/*.yaml',
            'icons/**/*.svg',
        ],
    },
    include_package_data=True,
    
    # Pin versions for better compatibility
    install_requires=[
        'reportlab>=3.6.0',
        'PyYAML>=5.4',
        'svglib>=1.2.0',
        'qrcode>=7.3',
        'Pillow>=8.0.0',
        'matplotlib>=3.3.0',
        'numpy>=1.19.0',
        'lxml>=4.6.0',
        'faker>=10.0',  
        'importlib_resources>=5.0; python_version<"3.9"',  # 
    ],
    
    # Classifiers help users find your package
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business",
        "Topic :: Text Processing :: Markup",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    
    entry_points={
        'console_scripts': [
            'resumate=resumate.cli:main',
        ],
    },
    
    # Additional metadata
    keywords='resume cv pdf yaml generator template beautiful professional',
    license='MIT',
)