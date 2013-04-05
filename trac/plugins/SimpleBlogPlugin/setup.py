from setuptools import setup

setup(
    name='SimpleBlogPlugin',
    version='0.1',
    author='Johann C. Rocholl',
    author_email='johann@browsershots.org',
    url='http://www.trac-hacks.org/wiki/SimpleBlogPlugin',
    description='Simple blogging plugin for Trac',
    license='BSD',
    packages=['simpleblog'],
    package_data = {'simpleblog' : ['templates/*.cs']},
    entry_points = {'trac.plugins': ['simpleblog = simpleblog']},
)
