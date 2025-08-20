import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="calflops2",
    version="0.1.0",
    author="Andrij David",
    author_email="david@andrij.me",
    description="A tool to calculate FLOPs and Params for neural networks",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrijdavid/calculate-flops.pytorch",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "torch",
        "torchvision",
        "transformers",
        "numpy",
        "accelerate",
    ],
)
