from setuptools import find_packages, setup

setup(name='energyPATHWAYS',
      version='2024.01.06',
      description='Software package for long-term energy system modeling',
      url='https://github.com/energyPATHWAYS/energyPATHWAYS',
      author='Ben Haley, Ryan Jones',
      packages=find_packages(),
      install_requires=['pandas',
                        'numpy',
                        'scipy',
                        'pint',
                        'pyomo',
                        'datetime',
                        'pytz',
                        'matplotlib',
                        'click',
                        'numpy_financial',
                        'sphinx_rtd_theme',
                        ],
      extras_require={'documentation': ["Sphinx"],
                      },
      include_package_data=True,
      entry_points={'console_scripts': ['energyPATHWAYS=energyPATHWAYS.run:click_run',
                                        'EP2RIO=energyPATHWAYS.export_to_rio:click_run']},
)
