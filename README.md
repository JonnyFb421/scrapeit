What is ScrapeIt?
===
ScrapeIt is a configuration driven web scraping python framework. The goal is to easily retrieve data from a web page and return the content.  


Config Example
---
`example.yaml`
```yaml
python_website:
  'urls':
    homepage: https://www.python.org/
  'selector': ['div', "class": "jobs-widget"]
  'selector_is_unique': true
  'use_regex': true
  'match_after': ['Jobs']
  'stop_matching_at': ['']
#  match_after_strftime: ['%A, %b %d, %Y', '', 0]
#  stop_matching_at_strftime: ['%A, %b, %d %Y', 1]
#  timezone: 'America/Los_Angeles'

```

Usage Example
---
```python
import os

from ruamel import yaml

import scrapeit


config_file = os.path.join('config', 'example.yaml')
with open(config_file) as file:
    config = yaml.safe_load(file)

text = scrapeit.get_text('homepage', **config['python_website'])
print(text)
```
```
Out: "Looking for work or have a Python related position that you're trying to hire for? Our relaunched community-run job board is the place to go.jobs.python.org"
```
Limitations
---
ScrapeIt is currently not equipped to handle auth. 

The only data ScrapeIt currently is able to retrieve is text. 
