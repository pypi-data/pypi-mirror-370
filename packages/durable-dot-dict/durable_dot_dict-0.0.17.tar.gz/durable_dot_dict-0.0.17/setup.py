from setuptools import setup

with open("README.md", "r",encoding="utf-8") as fh:
    long_description = fh.read()



setup(
    name='durable_dot_dict',
    version='0.0.17',
    description='Durable Dot Dictionary',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Risto Kowaczewski',
    packages=['durable_dot_dict'],
    install_requires=[
        'dotdict_parser'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=['durable_dot_dict'],
    include_package_data=True,
    python_requires=">=3.10",
)
