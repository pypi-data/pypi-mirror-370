from setuptools import setup

setup(
    name="djina",
    packages=["djina"],
    version="0.1.2",
    license="MIT",
    description="Djina's Python API",
    author="Nelson Monteiro",
    author_email="nelson@djina.com",
    url="https://github.com/djinalab/djina-python-api",
    keywords=["Djina", "SymbolicAI"],
    install_requires=[
        "requests",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Database :: Front-Ends",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
