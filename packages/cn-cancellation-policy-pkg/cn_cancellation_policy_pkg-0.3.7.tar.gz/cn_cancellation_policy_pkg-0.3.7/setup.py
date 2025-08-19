from setuptools import setup, find_packages

setup(
    name="cn_cancellation_policy_pkg",
    version="0.3.7",
    packages=find_packages(),
    install_requires=[
    ],
    test_suite='tests',
    author="Khalil Raza",
    author_email="khalilraza49@gmail.com",
    description="A library for parsing cancellation policies",
    keywords="cancellation policy parser",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
