from setuptools import setup, find_packages

setup(
    name="vindioai",
    version="0.2.2",
    author="Vindio AI Software Ltd. - Cem Direkoglu and Melike Sah", 
    author_email="vindioai@gmail.com",
    description="Quantum Vision Theory in Deep Learning for Object Recognition",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vindioai/QVBlock",
    packages=find_packages(),
    install_requires=[
        "tensorflow>=2.0.0",
        "numpy>=1.19.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
