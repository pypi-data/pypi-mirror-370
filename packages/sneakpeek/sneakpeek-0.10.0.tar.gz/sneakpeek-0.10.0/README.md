
<div align="center">
  <h1>
    SneakPeek
  </h1>
  <h4>A python module and a minimalistic server to generate link previews.</h4>
</div>

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://pepy.tech/badge/sneakpeek)](https://pepy.tech/project/sneakpeek)
[![PyPI](https://img.shields.io/pypi/v/sneakpeek)](https://pypi.org/project/sneakpeek)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sneakpeek)](https://pypi.org/project/sneakpeek)
[![test-ci](https://img.shields.io/github/workflow/status/codingcoffee/sneakpeek/test-ci)](https://github.com/codingCoffee/sneakpeek/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/codingcoffee/sneakpeek)](https://hub.docker.com/r/codingcoffee/sneakpeek)
[![Docker Image Size (tag)](https://img.shields.io/docker/image-size/codingcoffee/sneakpeek/latest)](https://hub.docker.com/r/codingcoffee/sneakpeek)

## What is supported

- Any page which supports [Open Graph Protocol](https://ogp.me) (which most sane websites do)
- Special handling for sites like
  - [Twitter](https://twitter.com) (requires a twitter [API key](https://developer.twitter.com/))


## Installation

Run the following to install

```sh
pip install sneakpeek
```


## Usage as a Python Module

### From a URL

```sh
>>> import sneakpeek
>>> from pprint import pprint

>>> link = sneakpeek.SneakPeek("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
>>> link.fetch()
>>> link.is_valid()
True
>>> pprint(link)
{'description': 'The official video for “Never Gonna Give You Up” by Rick '
                'AstleyTaken from the album ‘Whenever You Need Somebody’ – '
                'deluxe 2CD and digital deluxe out 6th May ...',
 'domain': 'www.youtube.com',
 'image': 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg',
 'image:height': '720',
 'image:width': '1280',
 'scrape': False,
 'site_name': 'YouTube',
 'title': 'Rick Astley - Never Gonna Give You Up (Official Music Video)',
 'type': 'video.other',
 'url': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',
 'video:height': '720',
 'video:secure_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
 'video:tag': 'never gonna give you up karaoke',
 'video:type': 'text/html',
 'video:url': 'https://www.youtube.com/embed/dQw4w9WgXcQ',
 'video:width': '1280'}

>>> link = sneakpeek.SneakPeek(url="https://codingcoffee.dev")
>>> link.fetch()
>>> pprint(link)
{'description': 'A generalist with multi faceted interests and extensive '
                'experience with DevOps, System Design and Full Stack '
                'Development. I like blogging about things which interest me, '
                'have a niche for optimizing and customizing things to the '
                'very last detail, this includes my text editor and operating '
                'system alike.',
 'domain': 'codingcoffee.dev',
 'image': 'https://www.gravatar.com/avatar/7ecdc5e1441ecd501faaf42a6ab9d6c0?s=200',
 'scrape': False,
 'title': 'Ameya Shenoy',
 'type': 'website',
 'url': 'https://codingcoffee.dev'}
```

Use `scrape=True` to fetch data using scraping instead of relying on open graph tags

```sh
>>> link = sneakpeek.SneakPeek(url="https://news.ycombinator.com/item?id=23812063", scrape=True)
>>> link.fetch()
>>> pprint(link)
{'description': '',
 'domain': 'news.ycombinator.com',
 'image': 'y18.gif',
 'scrape': True,
 'title': 'WireGuard as VPN Server on Kubernetes with AdBlocking | Hacker News',
 'type': 'other',
 'url': 'https://news.ycombinator.com/item?id=23812063'}
 ```

### From HTML

```
>>> HTML = """
... <html xmlns:og="http://ogp.me/ns">
... <head>
... <title>The Rock (1996)</title>
... <meta property="og:title" content="The Rock" />
... <meta property="og:description" content="The Rock: Directed by Michael Bay. With Sean Connery, Nicolas Cage, Ed Harris, John Spencer. A mild-mannered chemist and an ex-con must lead the counterstrike when a rogue group of military men, led by a renegade general, threaten a nerve gas attack from Alcatraz against San Francisco.">
... <meta property="og:type" content="movie" />
... <meta property="og:url" content="http://www.imdb.com/title/tt0117500/" />
... <meta property="og:image" content="https://m.media-amazon.com/images/M/MV5BZDJjOTE0N2EtMmRlZS00NzU0LWE0ZWQtM2Q3MWMxNjcwZjBhXkEyXkFqcGdeQXVyNDk3NzU2MTQ@._V1_FMjpg_UX1000_.jpg">
... </head>
... </html>
... """
>>> movie = sneakpeek.SneakPeek(html=HTML)
>>> movie.is_valid()
True
>>> pprint(movie)
{'description': 'The Rock: Directed by Michael Bay. With Sean Connery, Nicolas '
                'Cage, Ed Harris, John Spencer. A mild-mannered chemist and an '
                'ex-con must lead the counterstrike when a rogue group of '
                'military men, led by a renegade general, threaten a nerve gas '
                'attack from Alcatraz against San Francisco.',
 'domain': None,
 'image': 'https://m.media-amazon.com/images/M/MV5BZDJjOTE0N2EtMmRlZS00NzU0LWE0ZWQtM2Q3MWMxNjcwZjBhXkEyXkFqcGdeQXVyNDk3NzU2MTQ@._V1_FMjpg_UX1000_.jpg',
 'scrape': False,
 'title': 'The Rock',
 'type': 'movie',
 'url': 'http://www.imdb.com/title/tt0117500/'}
```


## Usage as a Server

A simple server using FastAPI and uvicorn is used to serve the requests.

```sh
sneekpeek serve
```

You can view the docs at http://localhost:9000/docs


## Usage as a CLI

```
sneakpeek preview --url "https://github.com/codingcoffee/" | jq
{
  "domain": "github.com",
  "scrape": false,
  "url": "https://github.com/codingCoffee",
  "title": "codingCoffee - Overview",
  "type": "profile",
  "image": "https://avatars.githubusercontent.com/u/13611153?v=4?s=400",
  "description": "Automate anything and everything 🙋‍♂️. codingCoffee has 68 repositories available. Follow their code on GitHub.",
  "error": null,
  "image:alt": "Automate anything and everything 🙋‍♂️. codingCoffee has 68 repositories available. Follow their code on GitHub.",
  "site_name": "GitHub"
}
```

## Docker

### As a Server

```sh
docker run -it --rm -p 9000:9000 codingcoffee/sneakpeek -- serve --host 0.0.0.0
```

### As a CLI

```sh
docker run -it --rm -p 9000:9000 codingcoffee/sneakpeek -- preview --url "https://github.com/codingcoffee"
```


## Configuration

### Twitter

- Sign up for a developer account on twitter [here](https://developer.twitter.com/)
- Create an app
- Add the following variables as ENV vars


```
TWITTER_CONSUMER_KEY="sample"
TWITTER_CONSUMER_SECRET="sample"
TWITTER_ACCESS_TOKEN="sample"
TWITTER_ACCESS_TOKEN_SECRET="sample"
```


## Development

```
pip install -U poetry
git clone https://github.com/codingcoffee/sneakpeek
cd sneakpeek
poetry install
```


## Running Tests

```sh
poetry run pytest
```

- Tested Websites
  - [x] [YouTube](https://youtube.com)
  - [x] [GitHub](https://github.com)
  - [x] [LinkedIN](https://linkedin.com)
  - [x] [Reddit](https://reddit.com)
  - [x] [StackOverflow](https://stackoverflow.com)
  - [x] [Business Insider](https://www.businessinsider.in)
  - [x] [HackerNews](https://news.ycombinator.com/)
  - [x] [Twitter](https://twitter.com)


## TODO

- [ ] [Instagram](https://instagram.com) (using [instagram-scraper](https://github.com/arc298/instagram-scraper))
- [ ] [Facebook](https://facebook.com)
- [ ] https://joinfishbowl.com/post_v3ibj1p63t
- [ ] CI/CD for publishing to PyPi


## Contribution

Have better suggestions to optimize the server image? Found some typos? Need special handling for a new website? Found a bug? Go ahead and create an [Issue](https://github.com/codingcoffee/sneakpeek/issues)! Contributions of any kind welcome!

Want to work on a TODO? Its always a good idea to talk about what are going to do before you actually start it, so frustration can be avoided.

Some rules for coding:

- Use the code style the project uses
- For each feature, make a seperate branch, so it can be reviewed separately
- Use commits with a good description, so everyone can see what you did


## License

The code in this repository has been released under the [MIT License](https://opensource.org/licenses/MIT)

