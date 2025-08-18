from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("lexia/requirements.txt", "r", encoding="utf-8") as fh:
        requirements = []
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                requirements.append(line)
        return requirements

setup(
    name="lexia",
    version="1.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Clean, minimal package for Lexia platform integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/lexia",
    packages=find_packages(),
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
        "Programming Language :: Python :: 3.13",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Framework :: FastAPI",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-asyncio>=0.18.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "web": [
            "fastapi>=0.100.0",
            "uvicorn>=0.20.0",
        ],
    },
    include_package_data=True,
    package_data={
        "lexia": ["*.txt", "*.md"],
    },
    keywords="lexia, ai, chatbot, platform, integration, fastapi, real-time",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/lexia-platform/issues",
        "Source": "https://github.com/yourusername/lexia-platform",
        "Documentation": "https://github.com/yourusername/lexia-platform#readme",
    },
)
