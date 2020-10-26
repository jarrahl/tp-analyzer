from setuptools import setup, find_packages

setup(
    name="tp_analyzer",
    version="0.0.2",
    author="Nick James, Jarrah Lacko and Max Menzies",
    author_email="jarrah@lacko.com.au",
    description="A package to identify turning points in time series data",
    url="https://github.com/jarrahl/tp-analyzer",
    packages=find_packages(exclude=["tests*"]),
    package_data={"tp_analyzer": ["data/*.csv"]},
    install_requires=["sortedcontainers", "numpy", "scipy", "matplotlib"],
    setup_requires=["wheel"],
    python_requires=">=3",
    license="MIT License",
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
    #long_description=open("README.md").read(),
    #long_description_content_type="text/markdown",
)

