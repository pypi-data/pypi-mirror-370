from setuptools import setup, find_packages

try:
    with open('readme.md', 'r') as f:
        long_description = f.read()
except FileNotFoundError as e:
    long_description = "chainable is a simple pipeline-based interface for querying HTML/XML with BeautifulSoup."

setup(
    name="chainsoup",
    version="0.1.7",
    author="ThefCraft",
    author_email="sisodiyalaksh@gmail.com",
    url="https://github.com/thefcraft/chainsoup",
    description="A fluent, pipeline-based interface for querying HTML/XML with BeautifulSoup.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    keywords=[
        "beautifulsoup", "bs4", "scraping", 
        "parser", "html", "xml", "fluent", 
        "chainable", "pipeline"
    ],
    classifiers=[
        # Indicates the development status of the project.
        "Development Status :: 4 - Beta",

        # Specifies the intended audience.
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: XML",

        # The license for the project.
        "License :: OSI Approved :: MIT License",

        # Specifies that the project is OS-independent.
        "Operating System :: OS Independent",

        # The versions of Python that the project supports.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beautifulsoup4>=4.9.0"
    ],
)