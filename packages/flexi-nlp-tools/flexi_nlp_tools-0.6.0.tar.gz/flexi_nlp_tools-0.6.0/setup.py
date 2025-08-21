from setuptools import setup, find_packages

setup(
    name="flexi-nlp-tools",
    version="0.6.0",
    description="NLP toolkit based on the flexi-dict data structure, designed for efficient fuzzy search, with a focus on simplicity, performance, and flexibility.",
    author="Tetiana Lytvynenko",
    author_email="lytvynenkotv@gmail.com",
    license="MIT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords=[
        "fuzzy search", "flexi search", "nlp tools", "natural language processing",
        "text processing", "string matching", "phonetic matching", "language tools",
        "transliteration", "transliterator", "text conversion", "numeral converter",
        "text normalization", "linguistic tools", "rule-based transliteration"
    ],
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "pandas>=2.2.3,<2.3",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False,
    package_data={
        "flexi_nlp_tools.numeral_converter.resource": ["*.csv"],
    },
)
