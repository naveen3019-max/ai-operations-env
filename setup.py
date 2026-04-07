"""
Setup configuration for AI Operations Assistant Environment
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="ai-operations-env",
    version="1.0.0",
    author="AI Research Team",
    description="Production-grade OpenEnv-compliant environment for enterprise AI workflows",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-repo/ai-operations-env",
    packages=find_packages(),
    py_modules=["validate_openenv"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pydantic>=2.0.0",
        "pyyaml>=6.0",
        "python-dateutil>=2.8.0",
    ],
    entry_points={
        "console_scripts": [
            "ai-ops-baseline=baseline.run:cli_main",
            "openenv-validate=validate_openenv:main",
        ],
    },
)
