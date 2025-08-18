from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tspay-client",
    version="0.2.1",
    author="Muhammadakbar Komilov",
    author_email="support@tspay.uz",
    description="TSPay uchun rasmiy Python klienti",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tspayuz/tspay-client",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "requests>=2.25.1",
    ],
)