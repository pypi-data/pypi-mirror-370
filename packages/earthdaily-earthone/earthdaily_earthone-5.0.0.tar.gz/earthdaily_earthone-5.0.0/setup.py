#!/usr/bin/env python

# © 2025 EarthDaily Analytics Corp.
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

import ast
import re

from setuptools import find_namespace_packages, setup

# Parse the docstring out of earthone/__init__.py
_docstring_re = re.compile(r'"""((.|\n)*)\n"""', re.MULTILINE)
with open("earthdaily/earthone/__init__.py", "rb") as f:
    __doc__ = _docstring_re.search(f.read().decode("utf-8")).group(1)

DOCLINES = __doc__.split("\n")

# Parse version out of earthone/core/client/version.py
_version_re = re.compile(r"__version__\s+=\s+(.*)")
with open("earthdaily/earthone/core/client/version.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )


def do_setup():
    viz_requires = [
        "matplotlib>=3.1.2",
        "ipyleaflet>=0.17.2",
    ]
    tests_requires = [
        "pytest==6.0.0",
        "responses==0.12.1",
        "freezegun==0.3.12",
    ]
    setup(
        name="earthdaily-earthone",
        description=DOCLINES[0],
        long_description="\n".join(DOCLINES[2:]),
        author="EarthDaily",
        author_email="support.eds@earthdaily.com",
        url="https://github.com/earthone-python",
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Programming Language :: Python :: 3.12",
            "Programming Language :: Python :: 3.13",
        ],
        license="Apache 2.0",
        download_url=(
            "https://github.com/earthdaily/earthone-python/archive/v{}.tar.gz".format(
                version
            )
        ),
        version=version,
        packages=find_namespace_packages(include=["earthdaily.earthone*"]),
        package_data={
            "earthdaily.earthone": [
                "config/settings.toml",
            ]
        },
        include_package_data=True,
        entry_points={
            "console_scripts": [
                "earthone = earthdaily.earthone.core.client.scripts.__main__:main"
            ]
        },
        python_requires="~=3.10",
        install_requires=[
            "affine>=2.2.2",
            "blosc2>=3.6.1",
            "cachetools>=3.1.1",
            "click>=8.2.0",
            "dill>=0.3.6",
            "dynaconf>=3.2.1",
            "geojson>=2.5.0",
            "geopandas>=0.13.2",
            "imagecodecs>=2023.3.16",
            "lazy_object_proxy>=1.7.1",
            "mercantile>=1.1.3",
            "numpy>=2.0.0",
            "packaging>=25.0",
            "Pillow>=9.2.0",
            "pyarrow>=14.0.1",
            "pydantic>=2.4.0",
            "requests>=2.32.3,<3",
            "shapely>=2.0.0",
            "strenum>=0.4.8",
            "tifffile>=2023.9.26",
            "tqdm>=4.66.3",
            "urllib3>=1.26.19, !=2.0.0, !=2.0.1, !=2.0.2, !=2.0.3, !=2.0.4",
        ],
        extras_require={
            "visualization": viz_requires,
            "complete": viz_requires,
            "tests": tests_requires,
        },
        data_files=[("docs/earthone", ["README.md"])],
    )


if __name__ == "__main__":
    do_setup()
