from setuptools import setup


with open('README.md') as f:
    long_description = ''.join(f.readlines())


setup(
    name='swing_server',
    version='0.2',
    description='An open-source Swing chart repository server',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Jan Šafařík',
    author_email='cowjen01@gmail.com',
    keywords='docker,swarm,repository',
    license='Apache License 2.0',
    url='https://github.com/docker-swing/swing-server',
    packages=['swing_server'],
    install_requires=[
        'flask~=1.1.2',
        'python-dotenv~=0.15.0',
        'psycopg2~=2.8.6',
        'flask-login~=0.5.0',
        'flask-sqlalchemy~=2.4.4',
        'flask-session~=0.3.2',
        'pyyaml~=5.4.1',
        'werkzeug~=1.0.1'
    ],
    classifiers=[
        'Framework :: Flask',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    zip_safe=False,
)
