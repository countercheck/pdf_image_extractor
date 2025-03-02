from setuptools import setup, find_packages

setup(
    name="pdfimages",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pdf2image>=1.16.0",
        "Pillow>=9.0.0",
        "PyYAML>=6.0",
        "Click>=8.0.0",
        "tqdm>=4.62.0",
    ],
    entry_points={
        "console_scripts": [
            "pdfimages=pdfimages.__main__:main",
        ],
    },
    python_requires=">=3.8",
    author="Your Name",
    author_email="your.email@example.com",
    description="A command-line utility to extract all distinct images from PDF files",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/pdfimages",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
)