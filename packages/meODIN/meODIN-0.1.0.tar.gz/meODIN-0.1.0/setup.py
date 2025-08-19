from setuptools import setup, find_packages

setup(
    name="meODIN",
    version="0.1.0",
    description="Optical Design Integrated Network",
    author="Sebastian Gedeon",
    author_email="sebastian.gedeon@gmail.com",
    packages=find_packages(),
    install_requires=["requests"],
    python_requires=">=3.7",
    license="MIT",
    license_files=("LICENSE",),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
