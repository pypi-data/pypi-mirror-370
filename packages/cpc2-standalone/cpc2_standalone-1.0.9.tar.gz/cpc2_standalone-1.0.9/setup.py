import setuptools
import os
from setuptools.command.build_py import build_py
import subprocess

# Custom build command to compile libsvm
class CustomBuild(build_py):
    def run(self):
        # Run the original build command
        build_py.run(self)
        # Compile libsvm
        libsvm_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'libs', 'libsvm', 'libsvm-3.18')
        subprocess.check_call(['make'], cwd=libsvm_dir)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cpc2_standalone",
    version="1.0.9",
    author="Kang Y. J., Yang D. C., Kong L., Hou M., Meng Y. Q., Wei L., Gao G.",
    author_email="gaog@mail.cbi.pku.edu.cn", # Placeholder, original author email not readily available
    description="CPC2: A fast and accurate coding potential calculator based on sequence intrinsic features. This package is maintained by Pranjal Pruthi, BioinformaticsOnLine organization.",
    long_description=long_description + """

## About CPC2

Here are some example commands:

*   **To run a basic test:** `cpc2 -i data/example.fa -o test_output`
*   **To check the reverse strand:** `cpc2 -i data/example.fa -o test_output -r`
*   **To output the longest ORF:** `cpc2 -i data/example.fa -o test_output --ORF`
*   **To get help:** `cpc2 --help`

Coding Potential Calculator distinguishes protein-coding from non-coding RNAs based on the sequence features of the input transcripts. CPC2 is an updated version of CPC1, designed to be faster and more accurate in discriminating coding and non-coding transcripts.

### Input Requirements

CPC2 accepts RNA transcript sequences in both FASTA format and GTF/GFF/BED format.

**FASTA format:**
*   Size: Less than 100,000 lines in input box (online) and no line limitation in batch mode. Maximum upload file size is 50 Mb.
*   Name: Sequence names must begin with ‘>’. Characters after a blank space in the ID will be discarded.
*   Sequence: Only characters found in DNA and RNA sequences are allowed.

**GTF/GFF/BED format:**
*   Supported formats: BED6, BED12, GTF, and GFF.
*   Size: Less than 50,000 lines. Maximum upload file size is 50 Mb.
*   Supported genomes for GTF/GFF/BED: Human (hg38, hg19), Chimpanzee (panTro4), Mouse (mm10), Rat (rn6), Zebrafish (danRer7), Xenopus (xendTro3), Fruitfly (dm6).
*   Note: Inputting in BED format might slow down processing.

### Features
*   **Speed and Accuracy:** CPC2 employs a novel discriminative model based on sequence intrinsic features, making it significantly faster than CPC1 and other popular tools, while also offering superior accuracy.
*   **Species-Neutral:** The model used in CPC2 is species-neutral, making it suitable for analyzing transcriptomes from a wide range of organisms, including non-model organisms.
*   **Output:** Results include sequence ID, coding/noncoding classification, coding probability, scores for putative peptide length, Fickett TESTCODE score, putative isoelectric point, and ORF integrity.

For more detailed information on the web server, input/output formats, and additional features like BLAST integration, please refer to the original CPC2 documentation and publication.

## Maintained for PyPI by:
Pranjal Pruthi
Project Scientist,
BioinformaticsOnLine organization
Email: mail@pranjal.work

## Original Publication:
Kang Y. J., Yang D. C., Kong L., Hou M., Meng Y. Q., Wei L., Gao G. 2017. CPC2: a fast and accurate coding potential calculator based on sequence intrinsic features. Nucleic Acids Research 45(Web Server issue): W12–W16.
""",
    long_description_content_type="text/markdown",
    url="https://github.com/gao-lab/CPC2_standalone",
    maintainer="Pranjal Pruthi",
    maintainer_email="mail@pranjal.work",
    packages=setuptools.find_packages() + ['cpc2_standalone'],
    package_dir={'cpc2_standalone': '.'},
    package_data={
        'cpc2_standalone': [
            'data/*',
            'libs/libsvm/libsvm-3.18/*',
            'libs/libsvm/libsvm-3.18/java/*',
            'libs/libsvm/libsvm-3.18/java/libsvm/*',
            'libs/libsvm/libsvm-3.18/matlab/*',
            'libs/libsvm/libsvm-3.18/python/*',
            'libs/libsvm/libsvm-3.18/svm-toy/gtk/*',
            'libs/libsvm/libsvm-3.18/svm-toy/qt/*',
            'libs/libsvm/libsvm-3.18/svm-toy/windows/*',
            'libs/libsvm/libsvm-3.18/tools/*',
            'libs/libsvm/libsvm-3.18/windows/*',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Intended Audience :: Science/Research",
    ],
    python_requires='>=3.9,<3.14',
    install_requires=[
        'numpy',
        'biopython',
        'six',
    ],
    entry_points={
        'console_scripts': [
            'cpc2=bin.CPC2:main_cli',
            'cpc2_output_peptide=bin.CPC2_output_peptide:main_cli',
        ]
    },
    include_package_data=True,
    cmdclass={
        'build_py': CustomBuild,
    },
)
