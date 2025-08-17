from setuptools import setup, find_packages

setup(
    name="igprasad",
    version="0.1.7",
    packages=find_packages(),
    entry_points={
        "console_scripts": ["ig=ig.cli:main"],
    },
    install_requires=[
        # List any external libraries your code depends on
        # For this script, there are none, so we can leave this empty
    ],
    python_requires=">=3.10",
    description="A command-line tool to run predefined Python and R programs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="godl",
    url="https://github.com/igprasad09/pip-igprasad", # Replace with your GitHub URL
    license="MIT", # Choose a license for your project
    keywords="cli python r learning",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)