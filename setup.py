import setuptools

with open('README.rst', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='msgraph-sdk-python',
    version='0.0.1',
    description='SDK for Microsoft Graph',
    long_description=long_description,
    packages=setuptools.find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/microsoftgraph/msgraph-sdk-python'
)
