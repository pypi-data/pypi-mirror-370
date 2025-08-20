from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="smart-terminal-ai",
    version="2.0.1",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI-powered terminal assistant that converts natural language to shell commands",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/smart-terminal",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/smart-terminal/issues",
        "Source": "https://github.com/yourusername/smart-terminal",
        "Documentation": "https://github.com/yourusername/smart-terminal#readme",
    },
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=12.0.0",
        "prompt_toolkit>=3.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
        ],
    },
    entry_points={
        "console_scripts": [
            "smart-terminal=smart_terminal.main:main",
            "st=smart_terminal.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
) 