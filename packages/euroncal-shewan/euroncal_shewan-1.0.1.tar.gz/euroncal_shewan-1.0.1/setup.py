
from setuptools import setup,find_packages

setup(
    name='euroncal-shewan',
    version='1.0.1',
     author="Shewan Dagne",
      author_email= "shewan.dagne1@gmail.com",
    packages=find_packages(),
    description="A simple calculator package",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    python_requires='>=3.6',
    entry_points={
        "console_scripts": [
            "euroncal=euroncal.calculator:main",
        ],
    },
   
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)