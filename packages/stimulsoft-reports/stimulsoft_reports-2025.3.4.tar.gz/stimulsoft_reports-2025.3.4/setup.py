from setuptools import setup, find_packages

with open('README.md') as file:
    readmeFile = file.read()

setup(
    name = 'stimulsoft_reports',
    version = '2025.3.4',
    author = 'Stimulsoft',
    author_email = 'info@stimulsoft.com',
    description = 'A powerful and modern reporting tool for Python services.',
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
        'Topic :: Office/Business',
        'Topic :: Software Development'
    ],
    install_requires = ['stimulsoft-data-adapters==2025.3.4'],
    extras_require = {'ext': 'stimulsoft-data-adapters[ext]==2025.3.4'},
    packages = find_packages(include=['stimulsoft_reports', 'stimulsoft_reports.*']),
    package_data = {'stimulsoft_reports': ['**/localizations/*.xml', '**/scripts/*.js']},
    python_requires = '>=3.10'
)
