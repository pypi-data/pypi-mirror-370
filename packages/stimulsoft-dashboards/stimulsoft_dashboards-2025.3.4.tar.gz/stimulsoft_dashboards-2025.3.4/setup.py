from setuptools import setup, find_packages

with open('README.md') as file:
    readmeFile = file.read()

setup(
    name = 'stimulsoft_dashboards',
    version = '2025.3.4',
    author = 'Stimulsoft',
    author_email = 'info@stimulsoft.com',
    description = 'Data visualization in Python applications.',
    long_description = readmeFile,
    long_description_content_type = 'text/markdown',
    url = 'https://www.stimulsoft.com/en/products/dashboards-python',
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
    install_requires = ['stimulsoft-reports==2025.3.4'],
    extras_require = {'ext': 'stimulsoft-reports[ext]==2025.3.4'},
    packages = find_packages(include=['stimulsoft_dashboards', 'stimulsoft_dashboards.*']),
    package_data = {'stimulsoft_dashboards': ['**/scripts/*.js']},
    python_requires = '>=3.10'
)
