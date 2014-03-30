import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.txt')) as f:
    README = f.read()
with open(os.path.join(here, 'CHANGES.txt')) as f:
    CHANGES = f.read()

requires = ['kajiki', 'markdown', 'pyyaml']

setup(name='Reinvent',
      version='0.0',
      description='A static blog engine',
      long_description=README + '\n\n' + CHANGES,
      classifiers=[
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
      ],
      author='',
      author_email='',
      url='',
      keywords='web',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="reinvent",
      entry_points="""\
      [console_scripts]
      remake-blog = reinvent.script:remake_blog
      recreate-blog = reinvent.script:recreate_blog
      """,
      )
