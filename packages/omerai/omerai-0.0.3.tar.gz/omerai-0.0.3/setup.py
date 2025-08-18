from setuptools import setup, find_packages

setup(
    name="omerai",
    version="0.0.3",
    author="Omer",
    author_email="omertech1230@gmail.com",
    description="AI image generator — DreamRender",
    packages=find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
