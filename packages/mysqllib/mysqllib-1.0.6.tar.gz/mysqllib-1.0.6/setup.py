from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='mysqllib',
    version='1.0.6',
    description='Simple mysql database library',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Krzysztof Żyłka',
    author_email='krzysztofzylka@yahoo.com',
    install_requires=[
        'pymysql'
    ],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)