from setuptools import setup, find_namespace_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name='ionntxpred',
    version='1.2',
    description='IonNTxPred: Prediction and design of ion channel-impairing proteins using protein language models.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='GPL-3.0',
    url='https://github.com/raghavagps/IonNTxPred',
    author='Anand Singh Rathore',
    author_email='anandr@iiitd.ac.in, anandrathoreindia@gmail.com',
    packages=find_namespace_packages(where="src"),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'ionntxpred = ionntxpred.python_scripts.ionntxpred:main'
        ]
    },
    python_requires='>=3.9',
    include_package_data=True,
    package_data={
        'ionntxpred.python_scripts': [
            'data/*',
            'config/*',
            'dataset/*',
            'merci/*',
            'motif/*/*',
            '*.py',
            'blast_binaries/linux/*',
            'blast_binaries/mac/*',
            'blast_binaries/windows/*',
            'BLAST/na_all_db/*',
            'BLAST/k_all_db/*',
            'BLAST/ca_all_db/*',
            'BLAST/other_all_db/*',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Bio-Informatics"
    ],
)
