from setuptools import setup, find_packages
import io

import nheri_simcenter


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', '\n')
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)

long_description = read('README.md')

setup(
    name='nheri_simcenter',
    version=nheri_simcenter.__version__,
    url='http://nheri-simcenter.github.io/nheri_simcenter/',
    license='BSD License',
    author='Adam Zsarnóczay',
    tests_require=['pytest'],
    author_email='adamzs@stanford.edu',
    description='NHERI SimCenter Python Dependencies',
    long_description=long_description,
    long_description_content_type='text/markdown',
    #packages=['nheri_simcenter'],
    packages = find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=[
        'numpy==1.26.4',
        'scipy==1.12.0',
        'pandas==2.2.3',
        'pydantic==2.4',
        'geopandas==0.14.4',
        'momepy==0.6.0',
        'jupyter',
        'openpyxl',
        'tables',
        'openseespy',
        'scikit-learn',
        'plotly',
        'colorlover',
        'jpype1',
        'tqdm',
        'gpy==1.13.2',
        'emukit',
        'psutil',
        'numpy-stl',
        'pyredi',
        'pelicun==3.7.1',
        'rasterio',
        'ujson==5.9',
        'xlrd',
        'matplotlib==3.9.2',
        'chardet',
        'backtrace',
        'welib',
        'sympy',
        'openquake.engine==3.17.1',
        'h5py',
        'rewet',
        'pyvista[all]',
        'tapipy',
        'reverse_geocode',
        'contextily',
        'pandana',
        'dill==0.3.9',
        'pyogrio==0.10.0'
    ],
    classifiers = [
        'Programming Language :: Python',
        'Development Status :: 5 - Production/Stable',
        'Natural Language :: English',
        'Environment :: Console',
        'Framework :: Jupyter',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Scientific/Engineering',
        ],
    extras_require={
        'testing': ['pytest'],
    }
)