from setuptools import setup, find_packages

setup(
    name="turning-point-detection",
    version="0.0.1",
    author="Nick James, Jarrah Lacko and Max Menzies",
    author_email="jarrah@lacko.com.au",
    description="A package to identify turning points in time series data",
    #url="github.com url",
    packages=find_packages(),
    install_requires=["numpy", "scipy"],
    extras_require={"display": ["matplotlib"]},
    python_requires=">=3",
    #license="BSD License",
    keywords=[
        "change point detection",
        "turning points",
        "time series",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
    ],
    long_description="",
)

