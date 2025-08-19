from setuptools import setup, find_packages

setup(
    name="ExcelCSVParseHelper",
    version="1.1.1",
    author="Marcin Kowalczyk",
    description="Lightweight helper library for parsing and manipulating Excel and CSV files easily.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pandas>=2.0",
        "openpyxl>=3.1.5",
        "psutil; platform_system == 'Windows'",
        "pywin32; platform_system == 'Windows'",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
