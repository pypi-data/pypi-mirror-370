from setuptools import setup, find_packages

setup(
    name="coffy",
    version="0.2.4",
    author="nsarathy",
    description="Lightweight local NoSQL, SQL, and Graph embedded database engine",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "networkx>=3.0",
        "pyvis>=0.3.2",
    ],
    python_requires=">=3.7",
    include_package_data=True,
    license="MIT",
    license_files=["LICENSE"],
    urls={
        "Website": "https://coffydb.org",
        "Source": "https://github.com/nsarathy/coffy",
        "Bug Reports & Feature Requests": "https://github.com/nsarathy/coffy/issues",
        "Discussions": "https://github.com/nsarathy/coffy/discussions",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "coffy-sql=coffy.cli.sql_cli:sql_cli",
        ],
    },
)
