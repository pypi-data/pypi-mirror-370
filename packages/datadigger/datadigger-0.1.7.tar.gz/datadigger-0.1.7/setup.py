from setuptools import setup, find_packages

setup(
    name="datadigger",  # Name of your package
    version="0.1.7",  # Initial version
    install_requires=[
        # "pandas==2.0.2",
        # "beautifulsoup4==4.12.2",  # Ensure you're listing valid dependencies
        # "UnicodeDammit",  # Remove if it's incorrectly added
    ],
    author="Ramesh Chandra",
    author_email="rameshsofter@gmail.com",
    description="The package is geared towards automating text-related tasks and is useful for data extraction, web scraping, and text file management.",
    long_description=open('README.md').read(),  # Optional: include a README
    long_description_content_type="text/markdown",
    packages=find_packages(),  # This will find all the packages in your project
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
