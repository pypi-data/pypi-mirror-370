from setuptools import setup, find_packages


setup(
    name='copious',
    version='0.1.29',
    packages=find_packages(),
    description='A handy tool that make your day to day programming much easier. ',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='brianlan',
    author_email='brianlanbo@gmail.com',
    url='https://github.com/brianlan/copious',
    install_requires=[
        "numpy>=1.21.0",
        "scipy>=1.7.0", 
        "tqdm>=4.60.0",
        "matplotlib>=3.5.0",
        "pyyaml>=5.4.0",
        "opencv-python>=4.5.0",
        "polars>=0.19.0",
        "pypcd4>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
)
