from setuptools import setup, find_packages

setup(
    name="Buke_PypiMain",
    version="1.0.0",
    author="yesben",
    author_email="jh20212645@gmail.com",
    description="test source",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://eu4ng.tistory.com",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)

# python setup.py sdist bdist_wheel
# twine upload dist/*
