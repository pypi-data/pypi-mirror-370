from setuptools import setup, find_packages
import os
import shutil

# Copy submodule content into package before building
def copy_icon_files():
    """Copy icon files from submodules into the package."""
    icon_sources = [
        ('submodules/devicons/icons', 'resumate/icons/devicons'),
        ('submodules/simple-icons/icons', 'resumate/icons/simple-icons'),
        ('submodules/fontawesome/svgs', 'resumate/icons/fontawesome'),
        ('submodules/fluentui-system-icons/assets', 'resumate/icons/fluentui'),
        ('submodules/logos/logos', 'resumate/icons/logos'),
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
    version='0.1.0',
    packages=find_packages(),
    package_data={
        'resumate': [
            'templates/*.yaml',
            'icons/**/*.svg',

        ],
    },
    include_package_data=True,
    install_requires=[
        'reportlab',
        'pyyaml',
        'svglib',
        'qrcode',
        'Pillow',
        'matplotlib',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'resumate=resumate.cli:main',
        ],
    },
    author='Charles Watkins',
    author_email='chris@watkinslabs.com',
    url='https://github.com/chris17453/resumate/',
    description='Professional resume generator with customizable templates',
)


