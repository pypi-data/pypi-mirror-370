from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="redfishLiteApi",
    version="1.0.1",
    author="Jeffery Lin",
    author_email="jeffery12240122@gmail.com",
    description="A lightweight Redfish API command-line tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeffery12240122/redfishLiteAPI",
    py_modules=["redfishLiteApi"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
    install_requires=[
        "requests>=2.25.1"
    ],
    entry_points={
        'console_scripts': [
            'redfishLiteApi=redfishLiteApi:main',
        ],
    },
)
