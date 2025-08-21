from setuptools import setup

setup(name='koronascript',
      version='0.2.1',
      description='Wrapper around Korona modules for processing echosounder data',
      long_description=open('README.md').read(),
      long_description_content_type='text/markdown',
      url='https://github.com/CRIMAC-WP4-Machine-learning/CRIMAC-KoronaScript',
      author='Ketil Malde',
      author_email='ketil@malde.org',
      packages=['KoronaScript'],
      package_data={'': ['configuration/korona-info.json']},
      include_package_data=True,
      zip_safe=False)
