from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="sagemagic",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="AI algorithms collection: Genetic algorithms for 8-Queens and TSP, plus propositional logic and Bayes theorem implementations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/sagemagic",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=[
        "random2>=1.0.1",
    ],
    keywords="genetic-algorithm, artificial-intelligence, 8-queens, tsp, traveling-salesman, propositional-logic, bayes-theorem, machine-learning",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/sagemagic/issues",
        "Source": "https://github.com/yourusername/sagemagic",
    },
)