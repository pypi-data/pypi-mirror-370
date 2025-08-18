from setuptools import setup, find_packages

setup(
    name="onepiece-lang",
    version="0.1.5",  # Incremented from 0.1.4 to 0.1.5
    packages=find_packages(),
    py_modules=["onepiece_interpreter", "onepiece_playground"],
    install_requires=[
        "click>=8.0",  # For command-line interface
        "streamlit>=1.0",  # For the Streamlit playground
    ],
    entry_points={
        "console_scripts": [
            "onepiece=onepiece_interpreter:main",
            "onepiece-playground=onepiece_playground:main",  # Added entry point for Streamlit app
        ],
    },
    author="Hash",  # Replace with your name
    author_email="website2k5@gmail.com",  # Replace with your email
    description="OnePiece Language: A fun, themed programming language inspired by One Piece",
    long_description=open("README.md").read() if open("README.md", errors="ignore") else "A fun programming language inspired by One Piece.",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/onepiece-lang",  # Replace with your repo URL
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)