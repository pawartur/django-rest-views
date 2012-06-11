from distutils.core import setup

setup(
    name='django-rest-views',
    version='0.1.0',
    author='Artur Wdowiarski',
    author_email='arturwdowiarski@gmail.com',
    packages=['rest_views', 'rest_views.tests'],
    url='http://github.com/pawartur/django-rest-views/tree/master',
    license='LICENSE.txt',
    description="Simple RESTful views based on django's CBVs.",
    long_description=open('README.txt').read(),
    package_data = {
        'rest_views.tests': [
            'fixtures/*.json',
        ]
    },
)
