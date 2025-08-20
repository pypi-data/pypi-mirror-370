from setuptools import setup
from distutils.command.install import install
from setuptools.command.develop import develop

# PEP 517 builds do not have . in sys.path
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))


class install_kernel_spec_mixin:

    def install_kernel_spec(self):
        """
        Install the Jupyter kernel spec.

        .. NOTE::

            The files are generated, not copied. Therefore, we cannot
            use ``data_files`` for this.
        """
        from m2_kernel.install import install_kernel_assets

        install_kernel_assets(user=False, prefix=self.install_data)


class sage_install(install, install_kernel_spec_mixin):

    def run(self):
        install.run(self)
        self.install_kernel_spec()


class sage_develop(develop, install_kernel_spec_mixin):

    def run(self):
        develop.run(self)
        if not self.uninstall:
            self.install_kernel_spec()


setup(
    cmdclass={
        "develop":   sage_develop,
        "install":   sage_install,
        },
    packages=['m2_kernel'],
    # packages=find_packages(),
    include_package_data=False,
    package_data={'m2_kernel': [
        'assets/m2-mode/*', 'assets/m2-code/*', 'assets/m2-spec/*']},
)
