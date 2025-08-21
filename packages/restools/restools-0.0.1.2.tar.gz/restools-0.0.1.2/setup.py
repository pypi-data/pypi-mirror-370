#   Copyright (c) 2022 DeepEvolution Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import io
from restools import __version__
from setuptools import setup, find_packages

with io.open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='restools',
    version=__version__,
    author='WorldSimulator',
    author_email='',
    description=('Collection of useful tools for research paper'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitee.com/FutureAGI/ResearchTools',
    license="Apache",
    packages=[package for package in find_packages()
              if package.startswith('restools')],
    python_requires='>=3.7',
    install_requires=[
        'matplotlib>=2.2.3',
        'numpy>=1.16.4',
        'pyyaml'
    ],
    extras_require={},
    zip_safe=False,
)
