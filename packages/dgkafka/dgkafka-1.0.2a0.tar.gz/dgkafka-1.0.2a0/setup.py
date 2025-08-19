from setuptools import setup, find_packages


with open('README.md') as f:
    long_description = f.read()


setup(name='dgkafka',
      version='1.0.0a17',
      description='Ver.1.0.0',
      long_description=long_description,
      long_description_content_type='text/markdown',  # This is important!
      classifiers=[
                   'Development Status :: 5 - Production/Stable',
                   #'Development Status :: 3 - Alpha',
                   'License :: OSI Approved :: MIT License',
                   'License :: OSI Approved :: Apache Software License',
                   'Programming Language :: Python :: 3',
                   "Operating System :: OS Independent",
                   ],
      keywords='',
      url='https://gitlab.com/gng-group/dgkafka.git',
      author='Malanris',
      author_email='admin@malanris.ru',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'dglog>=1.0.0.1,<2.0.0',
          'confluent-kafka[avro]>=2.9.0'
      ],
      include_package_data=True,
      zip_safe=False)
