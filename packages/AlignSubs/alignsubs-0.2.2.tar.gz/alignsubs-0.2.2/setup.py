from setuptools import setup, find_packages


setup(
    name='AlignSubs',
    version='0.2.2',
    license='GPL-3.0',
    description='AlignSubs: Alignment Substitution Analyzer (for nucleotide and aminoacid substitutions)',
    author="Taner Karagol",
    author_email='taner.karagol@gmail.com',
    url='https://github.com/karagol-taner/Alignment-Substitution-Analyzer',
    keywords='Alignment, FASTA, Clustal, MSA',
    install_requires=[
          'biopython',
      ],
    packages=['AlignSubs'],
    package_dir={'AlignSubs': 'AlignSubs'},
    entry_points={'console_scripts': ['AlignSubs = AlignSubs.__main__:main']},
    include_package_data=True,

)
