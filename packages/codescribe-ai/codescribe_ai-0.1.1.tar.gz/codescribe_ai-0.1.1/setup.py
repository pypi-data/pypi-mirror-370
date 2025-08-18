from setuptools import setup, find_packages
import pathlib

HERE = pathlib.Path(__file__).parent

# Load long description
long_description = (HERE / "README.md").read_text(encoding="utf-8")

# Load dependencies
with open(HERE / "requirements.txt", encoding="utf-8") as f:
    install_requires = [
        line.strip()
        for line in f.readlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="codescribe-ai",
    version="0.1.1",
    author="Mahesh Yannawar",
    author_email="glory@gloryofm.online",
    description="AI-powered README generator for any codebase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Mahi1609/codescribe_ai",
    packages=find_packages(),  # Automatically finds codescribe_ai and submodules
    include_package_data=True,
    install_requires=install_requires,
    entry_points={
        "console_scripts": [
            "codescribe=codescribe_ai.cli:main",  # CLI command: `codescribe`
        ]
    },
    python_requires=">=3.8",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
