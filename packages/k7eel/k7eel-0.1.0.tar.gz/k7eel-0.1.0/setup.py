from setuptools import setup, find_packages

setup(
    name="k7eel",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "your-tool=your_package.main:main",
        ],
    },
    author="M5TL",
    description="K7EEL",
    python_requires=">=3.6",
)