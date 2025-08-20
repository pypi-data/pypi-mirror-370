from setuptools import find_packages, setup

with open('README.md', 'r') as f:
    long_description = f.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith('#')]

setup(
    name='momopy',
    version='0.0.5',
    description='Python wrapper for Mobile Money Providers',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sharhan Alhassan',
    author_email='sharhanalhassan@gmail.com',
    url='https://github.com/sharhan-alhassan/momopy',
    packages=find_packages(exclude=['tests']),
    install_requires=requirements,
    keywords='momo mobile-money python package library',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
