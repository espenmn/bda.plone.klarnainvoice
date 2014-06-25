import os
from setuptools import setup
from setuptools import find_packages


version = '0.1'
shortdesc = "Klarna Invoice for bda.plone.shop"

setup(
    name='bda.plone.klarnainvoice',
    version=version,
    description=shortdesc,
    classifiers=[
        'Environment :: Web Environment',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    author='Espen Moe-Nilssen',
    author_email='espen@medialog.no',
    license='GNU General Public Licence',
    packages=find_packages('src'),
    package_dir = {'': 'src'},
    namespace_packages=['bda', 'bda.plone'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
        'Plone',
        'bda.plone.shop',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
        ]
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
    )
