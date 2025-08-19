import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sturdy-stats-sdk",
    version="1.0.47",
    author="Kian Ghodoussi",
    author_email="ghodoussikian@gmail.com",
    description="SDK for the Sturdy Statistics API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://sturdystatistics.com",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.9',
    install_requires=['more-itertools', 'srsly', 'tenacity', 'pandas', 'numpy', 'requests'],
    extras_require={
        'regression': ['arviz', 'xarray', 'scipy'],
        'all': ['arviz', 'xarray', 'scipy'],
    },
)
