try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

# here = os.path.abspath( os.path.dirname( __file__ ) )
# README = open(os.path.join( here, 'README.rst' ) ).read()


requirements = [
    'Django>=2.0.7', 'django-filter>=2.0.7',
    'djangorestframework>=3.8.2',
    'drf-nested-routers>=0.90.2',
    'chibi>=0.22.1', 'chibi_donkey>=1.0.0', 'chibi_auth0>=0.1.0',
    'chibi_elasticsearch>=1.4.1',
]


setup(
    name='chibi_django',
    version='0.9.0',
    description='snippets and utilities for django',
    # long_description=README,
    license="WTFPL",
    author='dem4ply',
    author_email='',
    packages=find_packages(include=[
        'chibi_django', 'chibi_django.*',
        'chibi_user', 'chibi_user.*',
        'test_runners', 'test_runners.*' ] ),
    install_requires=requirements,
    dependency_links = [],
    url='https://github.com/dem4ply/chibi_django',
    zip_safe=False,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Programming Language :: Python',
        'Topic :: Utilities',
    ],
)
