from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mitake",
    version="0.9.0",
    author="tzangms",
    author_email="tzangms@gmail.com",
    description="Python library for Mitake SMS API - 三竹簡訊 Python SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tzangms/mitake",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    keywords="mitake sms api taiwan",
    project_urls={
        "Bug Reports": "https://github.com/tzangms/mitake/issues",
        "Source": "https://github.com/tzangms/mitake",
    },
)