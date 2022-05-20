import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycellar",
    version="0.1.0",
    author="Knut Andreas Kvåle",
    author_email="knut.a.kvale@gmail.com",
    description="Python wine cellar library management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/knutankv/pycellar",
    packages=setuptools.find_packages(),
    install_requires=['numpy', 'pandas'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
)
