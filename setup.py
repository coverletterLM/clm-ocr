"""
Setup configuration for CLOVA OCR PDF Processor
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name="clova-ocr-processor",
    version="0.1.0",
    description="NAVER CLOVA OCR API를 사용한 PDF 텍스트 추출 라이브러리",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="chaewonjeong",
    author_email="chaewon@example.com",
    url="https://github.com/notebookLM/clm-ocr",
    packages=find_packages(exclude=["tests", "examples", "docs"]),
    install_requires=[
        "requests>=2.32.0,<3.0.0",
        "pandas>=2.0.0,<3.0.0",
        "PyMuPDF>=1.23.0,<2.0.0",
        "python-dotenv>=1.0.0,<2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
        ],
    },
    python_requires=">=3.11",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="ocr pdf clova naver text-extraction korean-ocr",
)
