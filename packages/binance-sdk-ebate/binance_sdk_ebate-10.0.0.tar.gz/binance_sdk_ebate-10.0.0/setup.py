from setuptools import setup, find_packages

setup(
    name="binance-sdk-ebate",
	    version="10.0.0",
    author="TitifelBro47",
    author_email="titifel@example.com",
    description="Demo SDK for Binance rebate migration testing (safe PoC)",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/binance/binance-connector-python/blob/f1703c54c3059423a8568b2300597210b19b938e/clients/rebate/docs/migration_guide_rebate_sdk.md",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=["requests"],
)
