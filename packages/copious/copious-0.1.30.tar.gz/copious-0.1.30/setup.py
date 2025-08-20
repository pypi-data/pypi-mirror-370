from setuptools import setup, find_packages


setup(
    name='copious',
    version='0.1.30',
    packages=find_packages(),
    description='A handy tool that make your day to day programming much easier. ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='brianlan',
    author_email='brianlanbo@gmail.com',
    url='https://github.com/brianlan/copious',
    install_requires=[
        "numpy>=1.22",
        "scipy>=1.8",
        "tqdm>=4.62",
        "matplotlib>=3.5",
        "pyyaml>=6.0",
        "opencv-python>=4.6",
        "polars>=0.20",
        "pypcd4>=1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "twine",
        ],
    },
)
