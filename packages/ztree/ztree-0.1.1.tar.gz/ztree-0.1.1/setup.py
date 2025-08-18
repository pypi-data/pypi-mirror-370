from setuptools import setup, find_packages

setup(
    name="ztree",
    version = "0.1.0",
    packages=find_packages(),  # auto-discovers packages like mypackage/
    install_requires=[
        "numpy",
        "scikit-learn",
        "jpype1"
    ],
    author = "Eric Cheng",
    author_email = "ericrcheng7@gmail.com",
    description = "Subgroup Identification Tree using Java backend, Scikit compatible",
    long_description = open("README.md").read(),
    long_description_content_type = "text/markdown",
    license = "MIT",
    classifiers=[
        "Programming Language :: Python :: 3",
    ],
    python_requires = ">=3.8",
    include_package_data = True,
)