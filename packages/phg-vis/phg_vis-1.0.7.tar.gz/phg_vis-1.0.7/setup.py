from setuptools import setup, find_packages

setup(
    name='phg_vis', 
    version='1.0.7', 
    packages=find_packages(),
    include_package_data=True,
    description='A package for phg modeling language',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='romeosoft',
    author_email='18858146@qq.com', 
    url='https://github.com/panguojun/phg',
    classifiers=[ 
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.11',
    install_requires=[],
    package_data={
        'phg': ['phg.pyd'],
        '': ['vis/**/*'],
    },
)