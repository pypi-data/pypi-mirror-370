import os
from setuptools import setup, Extension
from setuptools.config import read_configuration
import versioneer

try:
    from Cython.Build import cythonize
    cython_installed = True
except ImportError:
    cythonize = lambda x, *args, **kwargs: x
    cython_installed = False

conf_dict = read_configuration('setup.cfg')


def resolve_extensions():
    extensions = []
    if os.name == 'nt':
        return extensions

    if cython_installed:
        cy_exts = cythonize([
            Extension(
                'deepfos.boost.pandas',
                ['deepfos/boost/pandas.pyx'],
                include_dirs=["deepfos/boost"],
            ),
            Extension(
                'deepfos.boost.jstream',
                ['deepfos/boost/jstream.pyx'],
                include_dirs=["deepfos/boost"],
            ),
        ])
        extensions.extend(cy_exts)
    else:
        c_exts = [
            # Extension(
            #     'deepfos.boost.pandas',
            #     ['deepfos/boost/pandas.c'],
            #     include_dirs=['deepfos/boost'],
            #     py_limited_api=True
            # ),
            Extension(
                'deepfos.boost.jstream',
                ['deepfos/boost/jstream.c'],
                include_dirs=['deepfos/boost'],
                py_limited_api=True
            ),
        ]
        extensions.extend(c_exts)
    return extensions


setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    ext_modules=resolve_extensions()
)
