from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="pymn",
    version="1.1.0",
    author="DevMoEiN",
    author_email="devmoein@pm.me",
    description="Simple and powerful Telegram bot framework for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DevMoEiN/PyMn",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications :: Chat",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=[
        "aiohttp>=3.8.0",
    ],
    keywords="telegram bot api python library async",
    project_urls={
        "Bug Reports": "https://github.com/DevMoEiN/PyMn/issues",
        "Source": "https://github.com/DevMoEiN/PyMn",
    },
)
