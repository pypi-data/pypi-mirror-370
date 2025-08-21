from setuptools import find_packages
from setuptools import setup


version = '4.2.12'

setup(
    name='Products.MeetingSeraing',
    version=version,
    description="PloneMeeting profile for city of Seraing",
    long_description=open("README.rst").read() + "\n" + open("CHANGES.rst").read(),
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='',
    author='Andre Nuyens',
    author_email='andre.nuyens@imio.be',
    url='http://www.imio.be/produits/gestion-des-deliberations',
    license='GPL',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    namespace_packages=['Products'],
    include_package_data=True,
    zip_safe=False,
    extras_require=dict(
        test=['unittest2',
              'zope.testing',
              'plone.testing',
              'plone.app.testing',
              'plone.app.robotframework',
              'Products.CMFPlacefulWorkflow',
              'zope.testing',
              'Products.PloneTestCase',
              'Products.PloneMeeting[test]'],
        templates=['Genshi', ]),
    install_requires=[
        'setuptools',
        'Products.CMFPlone',
        'Pillow',
        'Products.PloneMeeting',
        'Products.MeetingCommunes'],
    entry_points={},
)
