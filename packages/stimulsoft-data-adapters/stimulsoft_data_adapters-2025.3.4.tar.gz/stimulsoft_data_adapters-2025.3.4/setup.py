from setuptools import setup, find_packages

with open('README.md') as file:
    readmeFile = file.read()

with open('REQUIREMENTS.txt') as file:
    requiresFile = [text.strip() for text in file if text.strip()]

setup(
    name = 'stimulsoft_data_adapters',
    version = '2025.3.4',
    author = 'Stimulsoft',
    author_email = 'info@stimulsoft.com',
    description = 'Stimulsoft data adapters for Python.',
    long_description = readmeFile,
    long_description_content_type = 'text/markdown',
    url = 'https://www.stimulsoft.com/en/products/reports-python',
    license = 'https://www.stimulsoft.com/en/licensing/developers',
    classifiers=[
        'License :: Other/Proprietary License',
        'Framework :: Django',
        'Framework :: Flask',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Database',
        'Topic :: Software Development'
    ],
    install_requires = ['pyodbc', 'requests'],
    extras_require = {'ext': requiresFile},
    packages = find_packages(),
    python_requires = '>=3.10'
)
