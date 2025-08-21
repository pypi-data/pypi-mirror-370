from setuptools import setup

setup(name='ActivityStream',
      version='0.5.1',
      url='http://sf.net/p/activitystream',
      packages=['activitystream', 'activitystream.storage'],
      install_requires=['pymongo>=2.8'],
      python_requires='>=3.10',
      license='Apache License, http://www.apache.org/licenses/LICENSE-2.0',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 3.10',
          'Programming Language :: Python :: 3.11',
          'Programming Language :: Python :: 3.12',
          'Programming Language :: Python :: 3.13',
          'Programming Language :: Python :: 3.14',
          ],
      )
