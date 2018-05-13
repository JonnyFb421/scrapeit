from setuptools import setup

version = '1.0.6'

requirements = [
    'pytz>=2018.4',
    'requests>=2.18.4',
    'beautifulsoup4==4.6.0'

]
dev_requirements = [
      'pytest>=3.5.1'
]

setup(name='scrapeit',
      version=version,
      description='Configuration driven web scraping framework',
      author='Jonathon Carlyon',
      author_email='JonathonCarlyon@gmail.com',
      url='https://github.com/JonnyFb421/scrapeit',
      install_requires=requirements,
      extras_require={'dev': dev_requirements},
      packages=['scrapeit'],
      )
