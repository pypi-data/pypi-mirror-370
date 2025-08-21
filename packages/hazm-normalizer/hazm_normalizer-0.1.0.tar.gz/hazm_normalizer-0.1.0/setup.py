from setuptools import setup, find_packages

setup(
    name="hazm_normalizer",
    version="0.1.0",
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
)
