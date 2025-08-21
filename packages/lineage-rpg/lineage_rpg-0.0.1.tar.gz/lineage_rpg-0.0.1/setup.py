from setuptools import setup, find_packages

setup(
    name='lineage-rpg',
    version='0.0.1',
    package_dir={'lineage_rpg': 'source'},
    packages=['lineage_rpg', 'lineage_rpg.commands'],
    entry_points={
        'console_scripts': [
            'lineage-rpg=lineage_rpg.main:start_game',
        ],
    },    
    python_requires='>=3.6',
)