from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
   name='tsbuddy',
   version='0.0.19',
   packages=find_packages(),
   install_requires=[
       # Add dependencies here.
       # e.g. 'numpy>=1.11.1'
       'paramiko>=2.7.0',
       #'pandas>=1.0.0',
       #'openai>=0.27.0',
   ],
   entry_points={
       'console_scripts': [
           'ts-csv=src.tsbuddy:main',  # Run the main function in tsbuddy to convert tech_support.log to CSV
           'ts-extract=src.extracttar.extract_all:main',  # Run the main function in extract_all to extract tar files
           'ts-extract-legacy=src.extracttar:main',  # Run the main function in extracttar to extract tar files
           'aosdl=src.aosdl.aosdl:main',  # Run the main function in aosdl to download AOS
           'aosga=src.aosdl.aosdl:lookup_ga_build',  # Run lookup_ga_build function
           'aosup=src.aosdl.aosdl:aosup',  # Run AOS Upgrade function to prompt for directory name and reload option
           'tsbuddy=src.tsbuddy_menu:menu',  # New menu entry point
           'ts-log=src.logparser:main', # Run function to consolidate logs in current directory
           'ts-get=src.get_techsupport:main',  # Run the main function in get_techsupport to gather tech support data
           'ts-clean=clean_pycache:clean_pycache_and_pyc',  # Run the clean function to remove __pycache__ directories and .pyc files
           'ts-graph-hmon=src.analyze.graph_hmon:main',  # Entry point for HMON Graph Generator
       ],
   },
   long_description=long_description,
   long_description_content_type='text/markdown',
   description = "Tech Support Buddy is a versatile Python module built to empower developers and IT professionals in resolving technical issues. It provides a suite of Python functions designed to efficiently diagnose and resolve technical issues by parsing raw text into structured data, enabling automation and data-driven decision-making.",
   include_package_data=True,
)
