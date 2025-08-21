from setuptools import setup, find_packages

setup(
    name="crossformer",
    version="v1.5.0",
    author="Dr. Peipei Wu (Paul)",
    author_email="peipeiwu1996@gmail.com",
    description="CrossFormer for multivariate time series forecasting",
    long_description=open("README_package.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Sedimark/Surrey_AI",
    license="EUPL-1.2",
    packages=find_packages(
        include=["crossformer", "crossformer.*"],
    ),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=["torch", "lightning", "pandas"],
    extras_require={
        "dev": [
            "pytest",
        ],
    },
    include_package_data=True,
)
