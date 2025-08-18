from setuptools import setup, find_packages

setup(
    name='custos-labs',        
    version='0.2.4',
    description='AI Alignment & Oversight Guardian for safe model output evaluation',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    author='Sylvester Duah',
    author_email='dev@custoslabs.com',
    url='https://github.com/dev-77-sys',
    packages=find_packages(include=["custos", "custos.*"]),
    install_requires=[
        'requests>=2.31.0',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    python_requires='>=3.8',
)
