from setuptools import setup, find_packages

setup(
    name="imagescraper-mavi",
    version="0.1.2",
    author="MaviMods",
    author_email="your-email@example.com",
    description="A simple Python package to scrape images from Google, Bing, and Yahoo",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/MaviMods/imagescraper",
    packages=find_packages(),
    install_requires=[
        "requests",
        "pillow"
    ],
    entry_points={
        "console_scripts": [
            "imagescraper=imagescraper_mavi.scraper:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Internet :: WWW/HTTP :: Indexing/Search",
    ],
    python_requires=">=3.7",
)
