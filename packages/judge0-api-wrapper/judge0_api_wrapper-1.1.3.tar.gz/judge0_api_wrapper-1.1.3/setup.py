import pathlib

from setuptools import setup, find_packages

HERE = pathlib.Path(__file__).parent.resolve()
REQUIRED = (HERE / "requirements.txt").read_text().splitlines()

setup(
    name='judge0-api-wrapper',
    version='1.1.3',
    description='API wrapper for Judge0 service',
    long_description=(HERE / "README.md").read_text(),
    long_description_content_type='text/markdown',
    author='Fabul0n',
    author_email='fabulon@mail.ru',
    url='https://github.com/Fabul0n/judge0-api-wrapper',
    packages=find_packages(),
    install_requires=REQUIRED,
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
)