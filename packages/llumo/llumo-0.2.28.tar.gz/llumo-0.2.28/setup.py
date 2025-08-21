# setup.py
import os
from setuptools import setup, find_packages

# Cloud Build will set TAG_NAME from the git tag.
VERSION = os.environ.get("TAG_NAME", "0.0.1.dev0")

# PyPI expects PEP 440 compliant versions.
# If your git tags are like 'v1.0.0', strip the leading 'v'.
if VERSION.startswith("v"):
    VERSION = VERSION[1:]


# --- Requirements ---
# Read requirements from requirements.txt and filter out build dependencies
def read_requirements():
    try:
        with open("requirements.txt", encoding="utf-8") as f:
            requirements = []
            for line in f.read().splitlines():
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith("#"):
                    # Filter out build/dev dependencies
                    if not any(
                        dev_pkg in line.lower()
                        for dev_pkg in ["setuptools", "twine", "wheel", "build"]
                    ):
                        requirements.append(line)
            return requirements
    except FileNotFoundError:
        print("WARNING: requirements.txt not found. Using fallback requirements.")
        # Fallback requirements based on your requirements.txt
        return [
            "requests>=2.0.0",
            "python-socketio",
            "python-dotenv",
            "openai==1.75.0",
            "tqdm==4.67.1",
            "google-generativeai==0.8.5",
            "websocket-client==1.8.0",
            
        ]


install_requires = read_requirements()
print(f"Install requires: {install_requires}")  # Debug print

# --- Long Description ---
# Read the contents of your README file
long_description = ""
try:
    with open("README.md", encoding="utf-8") as f:
        long_description = f.read()
except FileNotFoundError:
    pass

setup(
    name="llumo",
    version=VERSION,
    description="Python SDK for interacting with the Llumo ai API.",
    author="Llumo",
    author_email="product@llumo.ai",
    url="https://www.llumo.ai/",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=install_requires,
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

print(f"Building version: {VERSION}")
