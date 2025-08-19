from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "LumeTT - Multi-platform TinTin++ MUD client with scalable GUI"

setup(
    name="lumett",
    version="2.0.6",
    author="Federico",
    description="Multi-platform TinTin++ MUD client with scalable GUI",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lumett",  # Update with your repo
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'lumett': [
            'data/*',
            'data/lib/*',
        ],
    },
    entry_points={
        'console_scripts': [
            'lumett=lumett.cli:main',
        ],
    },
    install_requires=[
        # Add dependencies if needed
    ],
    python_requires='>=3.6',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment :: Multi-User Dungeons (MUD)",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="mud client tintin++ gaming",
)
