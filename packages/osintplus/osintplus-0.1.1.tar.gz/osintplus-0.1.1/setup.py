from setuptools import setup, find_packages

setup(
    name='osintplus',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'requests',
        'python-whois'
    ],
    entry_points={
        'console_scripts': [
            'osintplus=osintplus.cli:main',
        ],
    },
    author='root10',
    description='Outil OSINT CLI sans API',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/hakersgenie/osintplus',
)
