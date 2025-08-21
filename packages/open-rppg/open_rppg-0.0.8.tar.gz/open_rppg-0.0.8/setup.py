from setuptools import setup, find_packages
import glob
print(find_packages())
setup(
    name="open-rppg",
    version="0.0.8",
    description="Open rPPG",
    long_description='',
    long_description_content_type="text/markdown",
    author="Kegang Wang",
    #author_email="your.email@example.com",
    #url="https://github.com/your/repo",
    
    packages=['rppg'],
    python_requires=">=3.9",
    install_requires=open(r"C:\Users\16252\OneDrive\code\open_rppg\requirements.txt").read().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent", 
    ],
    include_package_data=True,
    zip_safe=False,
    package_data={'rppg':['weights/*.*']}
)
