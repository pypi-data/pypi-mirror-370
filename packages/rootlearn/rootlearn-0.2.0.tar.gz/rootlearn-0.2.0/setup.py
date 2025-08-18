from setuptools import setup, find_packages


setup(
    name="rootlearn",  
    version="0.2.0",
    author="Pranjal Kumar",
    description="A simple Linear Regression implementation from scratch",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    packages=find_packages(),  # finds 'rootlearn' and its sub-packages
    install_requires=[
        "numpy",
        "pandas",
        "scikit-learn>=1.0.0"
    ],
    license="MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires='>=3.0',
)
