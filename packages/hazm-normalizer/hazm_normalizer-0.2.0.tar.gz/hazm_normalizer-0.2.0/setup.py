from setuptools import setup, find_packages

with open("README.md","r") as f:
    description = f.read()

setup(
    name="hazm_normalizer",
    version="0.2.0",
    packages=find_packages(),
    install_requires=[
        "nltk","flashtext"
    ],
    package_data={
        "hazm_normalizer": [
            "data/words.dat",
            "data/stopwords.dat",
            "data/verbs.dat",
            "data/iwords.dat",
            "data/iverbs.dat",
            "data/abbreviations.dat",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    long_description = description,
    long_description_content_type = "text/markdown"
)
