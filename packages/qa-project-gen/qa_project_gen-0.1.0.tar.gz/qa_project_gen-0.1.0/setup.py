from setuptools import setup, find_packages

setup(
    name='qa-project-gen',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'jinja2',
    ],
    entry_points={
        'console_scripts': [
            'qa-gen = qa_project_gen.main:main',
        ],
    },
    package_data={
        'qa_project_gen': ['templates/**/*.j2'],
    },
)
