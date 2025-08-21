from setuptools import setup, find_packages

setup(
    name="q1ram",  # Use hyphen for PyPI
    version="0.1.11",
    description="Q1RAM Python client for interacting with the Quantum RAM API",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Q1RAM",
    author_email="quantum1ram@gmail.com",
    url="",  # optional
    packages=find_packages(),
    install_requires=[
        "requests",
        "python-dotenv", 
        "qiskit>=2.0.0",
        "requests",
        "qiskit_qasm3_import",
        "pylatexenc",
        "pydantic",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
