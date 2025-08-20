from setuptools import setup


setup(
    packages=['m2_kernel'],
    # packages=find_packages(),
    include_package_data=False,
    package_data={'m2_kernel': [
        'assets/m2-mode/*', 'assets/m2-code/*', 'assets/m2-spec/*']},
)
