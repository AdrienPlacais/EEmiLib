from setuptools import find_packages, setup

setup(
    name="EEmiLib",
    version="0.0.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "matplotlib==3.9.1",
        "myst-parser==3.0.1",
        "nbsphinx==0.9.4",
        "numpy==2.0.0",
        "pandas==2.2.2",
        "PyQt5==5.15.10",
        "pytest==8.2.2",
        "setuptools==70.2.0",
        "sphinx-rtd-theme==2.0.0",
    ],
    entry_points={
        "console_scripts": [
            "eemilib-gui=gui.gui:main",
        ],
    },
    author="Adrien Plaçais",
    description="Easily fit Electron EMIssion models on experimental data.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)
