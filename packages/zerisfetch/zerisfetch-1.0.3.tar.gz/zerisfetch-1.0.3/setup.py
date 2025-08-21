from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="zerisfetch",
    version="1.0.3",
    author="Zeris Nik",
    author_email="Zerisfetch@gmail.com",
    description="A neofetch-like system information display tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lqq0161-sys/zerisfetch",  # ← Ваш реальный URL
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "zerisfetch=zerisfetch.main:cli",
        ],
    },
    keywords="system info neofetch linux debian ubuntu arch",
    project_urls={
        "Bug Reports": "https://github.com/lqq0161-sys/zerisfetch/issues",
        "Source": "https://github.com/lqq0161-sys/zerisfetch",
    },
)
