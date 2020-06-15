import os

from setuptools import find_packages, setup

if __name__ == '__main__':
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        long_description = f.read()

    setup(name='gdriveupload',
          url='https://github.com/njzjz/gdriveupload',
          author='Jinzhe Zeng',
          author_email='jzzeng@stu.ecnu.edu.cn',
          packages=find_packages(),
          python_requires='~=3.6',
          install_requires=['requests', 'tqdm'],
          entry_points={
              'console_scripts': ['gdriveupload=gdriveupload.upload:cmd'
                                  ]
          },
          use_scm_version=True,
          setup_requires=[
              'setuptools>=18.0',
              'setuptools_scm',
          ],
          long_description=long_description,
          long_description_content_type='text/markdown',
          version="0.0.1",
    )