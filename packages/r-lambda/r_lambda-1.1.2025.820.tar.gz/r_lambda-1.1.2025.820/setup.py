import setuptools

# pip3 install setuptools wheel
# python3 setup.py sdist bdist_wheel

# upload package to repository
# pip3 install twine
# twine upload --repository pypi dist/*

# pip install test-package
# 
# import r_lambda
# from r_lambda.docker import docker_image

with open("README.md", "r") as fh:
    description = fh.read()

setuptools.setup(
    name="r_lambda",
    version="1.1.2025.0820",
    author="xieguigang",
    author_email="xie.guigang@gcmodeller.org",
    packages=["r_lambda"],
    description="A simple commandline wrapper package for call a target R# function from commandline",
    long_description=description,
    long_description_content_type="text/markdown",
    url="https://github.com/rsharp-lang/IronR",
    license='MIT',
    python_requires='>=3.6',
    install_requires=[]
)