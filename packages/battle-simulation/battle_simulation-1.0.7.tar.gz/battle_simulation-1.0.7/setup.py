from setuptools import setup, find_packages

setup(
    name="battle_simulation",  # Name of the package
    version="1.0.7",  # Incremented version
    author="Christian Johnson",
    author_email="cjohnson@metisos.com",
    description="A battle simulation package for strategic resource deployment.",
    long_description=open("README.md").read(),  # Optional: Include README content
    long_description_content_type="text/markdown",
    packages=find_packages(),  # Automatically find all sub-packages
    include_package_data=True,  # Include non-Python files (like models)
    package_data={
        'battle_simulation': ['models/*.pkl'],  # Specify .pkl files to include
    },
    install_requires=["numpy", "scikit-learn", "joblib"],  # Dependencies
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",  # Minimum Python version required
)
