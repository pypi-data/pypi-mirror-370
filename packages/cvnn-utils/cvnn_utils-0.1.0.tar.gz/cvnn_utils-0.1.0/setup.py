from setuptools import setup, find_packages

setup(
    name="cvnn-utils",
    version="0.1.0",
    description="A lightweight, principled toolkit for Complex-Valued Neural Networks in PyTorch.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="KrisTHL181",
    url="https://github.com/KrisTHL181/cvnn-utils",
    license="MIT",
    packages=find_packages(),
    install_requires=[
        "torch>=1.8.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
    keywords="deep learning, complex-valued, neural network, cvnn, pytorch",
)
