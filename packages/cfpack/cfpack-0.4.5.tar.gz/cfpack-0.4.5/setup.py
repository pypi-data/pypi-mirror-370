from setuptools import setup, find_packages

setup(
    name="cfpack",
    version="0.4.5",
    author="Christoph Federrath",
    author_email="christoph.federrath@anu.edu.au",
    description="Christoph Federrath (CF) python package (cfpack)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://www.mso.anu.edu.au/~chfeder/codes/cfpack/cfpack.html",
    project_urls={
        "Source": "https://github.com/chfeder/cfpack",
        "Documentation": "https://www.mso.anu.edu.au/~chfeder/codes/cfpack/doc/index.html",
    },
    license="MIT",
    license_file="LICENSE",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=find_packages(),
    python_requires='>=3',
    install_requires=[
        'astropy',
        'colorama',
        'corner',
        'emcee',
        'ipdb',
        'lmfit',
        'matplotlib',
        'numpy',
        'Pandas',
        'scipy',
    ],
)
