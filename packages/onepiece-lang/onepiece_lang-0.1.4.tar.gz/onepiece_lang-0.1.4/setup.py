from setuptools import setup, find_packages

setup(
    name="onepiece-lang",
    version="0.1.4",
    packages=find_packages(),
    py_modules=["onepiece_interpreter"],
    install_requires=["click"],
    entry_points={
        "console_scripts": [
            "onepiece=onepiece_interpreter:main",
        ],
    },
)
