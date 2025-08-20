from setuptools import setup, find_packages

setup(
    name='openvancy',
    version='0.0.0.8',
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
    'ovito',
    'pyvista',      # el core de PyVista
    'pyvistaqt',    # el wrapper Qt para PyVista
    'vtk'          # motor de renderizado de PyVista
],

    entry_points={
        "console_scripts": [
            "openvancy = vfscript.vfs_win:main"
        ]}
,
    include_package_data=True,
)
