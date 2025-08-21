# scrapesession

<a href="https://pypi.org/project/scrapesession/">
    <img alt="PyPi" src="https://img.shields.io/pypi/v/scrapesession">
</a>

A requests session meant for scraping with caching, backoffs and historical fallbacks.

## Dependencies :globe_with_meridians:

Python 3.11.6:

- [numpy](https://numpy.org/)
- [requests-cache](https://requests-cache.readthedocs.io/en/stable/)
- [wayback](https://github.com/edgi-govdata-archiving/wayback)
- [func-timeout](https://github.com/kata198/func_timeout)
- [random_user_agent](https://github.com/Luqman-Ud-Din/random_user_agent)
- [tenacity](https://github.com/jd/tenacity)
- [playwright](https://playwright.dev/)

## Raison D'être :thought_balloon:

`scrapesession` is a requests session that performs heavy caching and other tools in order to efficiently scrape sites.

## Architecture :triangular_ruler:

`scrapesession` is a requests session that has the following properties:

1. Handle non 302 redirects (such as in javascript).
2. Retries and backoffs.
3. User-Agent rotations.
4. Caching.
5. Wayback Machine integration.

## Installation :inbox_tray:

This is a python package hosted on pypi, so to install simply run the following command:

`pip install scrapesession`

or install using this local repository:

`python setup.py install --old-and-unmanageable`

## Usage example :eyes:

The use of `scrapesession` is entirely through code due to it being a library. It has exactly the same semantics as a requests session:

```python
from scrapesession.scrapesession import create_scrape_session


session = create_scrape_session()

response = session.get("http://www.helloworld.com")
print(response.text)
```

## License :memo:

The project is available under the [MIT License](LICENSE).
