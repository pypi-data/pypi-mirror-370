from setuptools import setup, find_packages

setup(
    name='svcmanagement',
    version='1.0.0',
    description='A library to manage hidden service files by downloading, verifying, and running them.',
    author='Nezura',
    author_email='nezur4@proton.me',
    url='https://github.com/shinecheeseemwith556s/pywtf',  # Update with your repo
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)