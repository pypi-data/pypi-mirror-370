import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    lng_description = fh.read()

setuptools.setup(
    name="Tonviewer",
    version="3.0",
    author="deep",
    author_email="asyncpy@proton.me",
    license="MIT",
    description="TON Crypto Info Scraper is a Python library without needing any APIs",
    long_description=lng_description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
