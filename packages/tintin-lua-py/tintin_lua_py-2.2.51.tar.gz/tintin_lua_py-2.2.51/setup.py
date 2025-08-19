from setuptools import setup, find_packages
import os

# Read README for long description
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "TinTin++ MUD client with Lua and Python scripting support"

setup(
    name="tintin-lua-py",
    version="2.02.51",
    author="Federico",
    description="TinTin++ MUD client with Lua and Python scripting support",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/tintin-lua-py",  # Update with your repo
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'tintin_lua_py': [
            'bin/tt++',
        ],
    },
    entry_points={
        'console_scripts': [
            'tt++=tintin_lua_py.cli:main',
            'tintin-lua-py=tintin_lua_py.cli:main',
        ],
    },
    install_requires=[
        # Add Python dependencies if needed
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
        "Programming Language :: C",
        "Programming Language :: Lua",
    ],
    keywords="mud client tintin++ gaming lua python scripting",
)
