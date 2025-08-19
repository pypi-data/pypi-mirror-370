# based on https://realpython.com/pypi-publish-python-package
# How to upload:
#  - change package version in `setup.py` and `__init__.py`
#  - `python setup.py sdist`
#  - `twine upload dist/arx-tools-?.tar.gz`
import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

# This call to setup() does all the work
setup(
    name='arx-tools',
    version='1.0.0',
    description='Set of scripts to aid Arx administrators import data',
    long_description=README,
    long_description_content_type='text/markdown',
    url='https://github.com/Abrinca/arx-tools',
    author='Abrinca',
    author_email='info@abrinca.com',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
    packages=['arx_tools'],
    include_package_data=True,  # see MANIFEST.in
    install_requires=['schema', 'biopython', 'termcolor', 'fire', 'pyyaml'],
    entry_points={
        'console_scripts': [
            'init_folder_structure=arx_tools.init_folder_structure:main',
            'import_genome=arx_tools.import_genome:main',
            'download_ncbi_genome=arx_tools.download_ncbi_genome:main',
            'genbank_to_fasta=arx_tools.genbank_to_fasta:main',
            'reindex_assembly=arx_tools.reindex_assembly:main',
            'rename_custom_annotations=arx_tools.rename_custom_annotations:main',
            'rename_eggnog=arx_tools.rename_eggnog:main',
            'rename_fasta=arx_tools.rename_fasta:main',
            'rename_genbank=arx_tools.rename_genbank:main',
            'rename_gff=arx_tools.rename_gff:main',
            'init_orthofinder=arx_tools.init_orthofinder:main',
            'import_orthofinder=arx_tools.import_orthofinder:main',
            'folder_looper=arx_tools.folder_looper:main',
            'update_folder_structure=arx_tools.update_folder_structure:main',
        ]
    },
)
