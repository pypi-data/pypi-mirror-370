from setuptools import setup, find_packages

# Read requirements.txt
with open('requirements.txt') as f:
    required = f.read().splitlines()

# Include requirements.txt in package data
setup(
    name='universal_timeseries_transformer',
    version='0.3.9',
    packages=find_packages(),
    install_requires=required,
    author='June Young Park',
    author_email='juneyoungpaak@gmail.com',
    description='A package for transforming and manipulating time series data with universal interfaces',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/nailen1/universal_timeseries_transformer',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    python_requires='>=3.8',
    data_files=[('', ['requirements.txt'])],
)