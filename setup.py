from setuptools import setup


setup(name='notabene',
    python_requires='>=3.8',
    version='0.0.1',
    description='Nota Bene Book',
    url='https://github.com/RoyBebru/notabene',
    author='Roy Bebru',
    author_email='RoyBebru@Gmail.Com',   ### Script Name After Installation
    license='MIT',                       #    ### Import module which must be called
    include_package_data=True,           #    #             ### Function call from module
    packages=["notabene"],               #    #             #
    entry_points = {'console_scripts': 'nb = notabene.main:main'})
