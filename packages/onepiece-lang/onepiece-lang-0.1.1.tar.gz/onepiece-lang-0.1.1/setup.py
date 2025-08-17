from setuptools import setup, find_packages

setup(
    name="onepiece-lang",
    version="0.1.1",  # incremented version
    packages=find_packages(),
    install_requires=[],
    entry_points={
        "console_scripts": [
            "onepiece=onepiece_interpreter:main",
        ],
    },
)
