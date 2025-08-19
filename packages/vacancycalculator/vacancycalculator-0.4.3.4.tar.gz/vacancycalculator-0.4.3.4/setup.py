from setuptools import setup, find_packages

setup(
    name='vacancycalculator',
    version='0.4.3.4',
    author='E.Bringa-S.Bergamin-SiMaF',
    author_email='santiagobergamin@gmail.com',
    license='MIT',
    description='Defect analysis and vacancy calculation for materials science',
    url='https://github.com/TiagoBe0/VFScript-SiMaF',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
    'numpy',
    'scipy',
    'pandas',
    'scikit-learn',
    'xgboost',
    'ase',
    'ovito',
    'pyvista',     
    'pyvistaqt',  
    'vtk'         
],

    entry_points={
        "console_scripts": [
            "vacancyfinder = vfscript.vfs_win:main"
        ]}
,
    include_package_data=True,
)
