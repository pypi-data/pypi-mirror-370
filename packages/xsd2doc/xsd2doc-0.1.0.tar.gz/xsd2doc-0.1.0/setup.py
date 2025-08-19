from setuptools import setup, find_packages

setup(
    name='xsd2doc',
    version='0.1.0',
    packages=find_packages(include=['xsd2doc', 'xsd2doc.*']),
    include_package_data=True,
    package_data={
        "xsd2doc": ["templates/*.j2"]
    },
    install_requires=[
        'lxml',
        'pyyaml',
        'jinja2',
        'argparse',
        'rich',
    ],
    entry_points={
        'console_scripts' : [
            'xsd2doc=xsd2doc.main:main'
        ]
    },
    author='YammyToast',
    description='xsd2doc: A tool to generate markdown documentation from XSD files',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
    ],
    python_requires='>=3.9'
)