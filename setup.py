try:
    from setuptools import setup, find_packages
except:
    from distutils.core import setup, find_packages

# here = os.path.abspath( os.path.dirname( __file__ ) )
# README = open(os.path.join( here, 'README.rst' ) ).read()

setup(
    name='chibi_django',
    version='0.1',
    description='',
    # long_description=README,
    license='',
    author='',
    author_email='',
    packages=find_packages(),
    install_requires=[
        'Django>=2.0.7', 'django-filter>=2.0.7',
        'djangorestframework>=3.8.2',
        'django-filters>=0.2.1', 'drf-nested-routers>=0.90.2',
        'social-auth-app-django>=2.1.0',
    ],
    dependency_links = [],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
    ],
)
