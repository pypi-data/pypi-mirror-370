from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="git-operations-tool",
    version="0.2.3",
    author="Dhanushkumar R",
    author_email="danushidk507@gmail.com",
    description="A comprehensive Git operations tool with advanced features including auto-commit with timing controls",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Idk507/git_operations_tool",
    project_urls={
        "Bug Tracker": "https://github.com/Idk507/git_operations_tool/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Version Control :: Git",
    ],
    packages=find_packages(),
    python_requires=">=3.7",
    install_requires=[
        "gitpython>=3.1.30",
        "requests>=2.28.1",
    ],
    entry_points={
        "console_scripts": [
            "git-ops=git_operations_tool.main:run_tool",
        ],
    },
)