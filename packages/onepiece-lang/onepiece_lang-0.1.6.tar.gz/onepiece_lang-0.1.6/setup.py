from setuptools import setup, find_packages

setup(
    name="onepiece-lang",
    version="0.1.6",  # Incremented to 0.1.5 as specified
    packages=find_packages(),
    py_modules=["onepiece_interpreter", "onepiece_playground"],
    install_requires=[
        "click>=8.0",  # For command-line interface
        "streamlit>=1.0",  # For the Streamlit playground
    ],
    entry_points={
        "console_scripts": [
            "onepiece=onepiece_interpreter:main",
            "onepiece-playground=onepiece_playground:main",
        ],
    },
    author="Hash",  # Your name
    author_email="website2k5@gmail.com",  # Your email
    description="OnePiece Language: A fun, themed programming language inspired by One Piece",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/onepiece-lang",  # Replace with your actual repository URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    include_package_data=True,  # Include non-code files like README.md
    keywords=["programming-language", "one-piece", "interpreter", "streamlit"],
)