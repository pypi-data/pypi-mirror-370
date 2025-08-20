import os

from setuptools import setup, find_packages

from security.version import get_version


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name='skip-django-security-logger',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    version=get_version(),
    description="Django security library.",
    keywords='django, throttling',
    author='Lubos Matl',
    author_email='matllubos@gmail.com',
    url='https://github.com/skip-pay/django-security',
    license='MIT',
    package_dir={'security': 'security'},
    include_package_data=True,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: Czech',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
    install_requires=[
        'django>=4.2',
        'django-ipware>=3.0.2',
        'ansi2html>=1.6.0',
        'skip-django-chamber>=0.7.2',
        'skip-django-choice-enumfields>=1.1.3.2',
        'skip-django-generic-m2m-field>=0.1.0',
        'skip-django-celery-extensions>=0.1.0',
        'isodate>=0.6.1',
        'structlog>=24.4.0',
    ],
    zip_safe=False
)
