from setuptools import find_packages, setup
from glob import glob

scripts = glob("scripts/*")
scripts = [script for script in scripts if script[-1] != '~']

setup(name="xastools",
      use_scm_version=True,
      setup_requires=['setuptools_scm'],
      install_requires=['numpy'],
      description="xastools",
      author="Charles Titus",
      platforms=["any"],
      scripts=scripts,
      packages=find_packages()
)
