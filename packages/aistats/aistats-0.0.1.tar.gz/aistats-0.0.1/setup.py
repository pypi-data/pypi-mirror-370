from setuptools import setup, find_packages

# ✅ Read long description using UTF-8
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="aistats",
    version="0.0.1",
    author="Rohit Kumar Behera",
    author_email="rohitmbl24@gmail.com",
    description="A Python package for descriptive and advanced statistical analysis",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Important for PyPI formatting
    packages=find_packages(),
    install_requires=["numpy",
        "scipy",
        "matplotlib",
        "pandas"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    license="MIT",
)
