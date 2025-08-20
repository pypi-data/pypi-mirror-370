# encoding: utf-8

"""Module for SneakPeek."""

# standard imports
import json
import re
import urllib.request
from urllib.parse import urlparse
from urllib.request import urlopen

# third-party imports
import validators
import yt_dlp as ydl
from bs4 import BeautifulSoup
from loguru import logger


class SneakPeek(dict):
    """ """

    required_attrs = ["title", "type", "image", "url", "description"]

    def __init__(self, url=None, html=None, scrape=False, **kwargs):
        # If scrape == True, then will try to fetch missing attribtues
        # from the page's body
        self.domain = None
        self.scrape = scrape
        self.url = url

        self.title = ""
        self.type = ""
        self.image = ""
        self.description = ""

        self.error = None

        for k in kwargs.keys():
            self[k] = kwargs[k]

        if url:
            self.is_valid_url(url)
            self.domain = urlparse(self.url).netloc

        if html is not None:
            self.parse(html)

    def __setattr__(self, name, val):
        self[name] = val

    def __getattr__(self, name):
        return self[name]

    def is_valid_url(self, url=None):
        return validators.url(url)

    def fetch_and_parse_youtube(self):
        ydl_opts = {
            "quiet": True,
        }
        with ydl.YoutubeDL(ydl_opts) as ydl_youtube:
            try:
                info_dict = ydl_youtube.extract_info(self.url, download=False)
                self.title = info_dict.get("title")
                self.description = info_dict.get("description")
                self.title = info_dict.get("title")
                self.image = info_dict.get("thumbnail")
                self.type = "video.other"
            except ydl.utils.DownloadError:
                return

    def fetch_and_parse_twitter(self):
        if not isinstance(self.url, str):
            return
        if "status" in self.url:
            # tweet_id = int(self.url.split("status/")[-1].split("?")[0])
            username = self.url.split("/")[3]
            self.title = f"{username} on Twitter"
            self.type = "article"
            self.description = ""
            return
        elif self.url.strip("/").endswith(".com"):
            self.title = "Twitter"
            self.type = "website"
            self.description = "Social Network Company"
        else:
            username = self.url.strip("/").split("/")[-1]
            self.title = f"{username} on Twitter"
            self.type = "profile"
            self.description = ""

        self.image = "https://upload.wikimedia.org/wikipedia/commons/5/57/X_logo_2023_%28white%29.png"

    def fetch(self):
        """ """
        if self.domain in [
            "twitter.com",
            "mobile.twitter.com",
            "www.twitter.com",
            "x.com",
        ]:
            return self.fetch_and_parse_twitter()
        if self.domain in ["youtube.com", "www.youtube.com"]:
            return self.fetch_and_parse_youtube()
        if not isinstance(self.url, str):
            return
        # TODO: use random user agent for every request - https://github.com/Luqman-Ud-Din/random_user_agent
        req = urllib.request.Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urllib.request.urlopen(req) as raw:
                html = raw.read()
        except Exception as err:
            logger.debug("Unable to fetch data for URL")
            html = ""
            self.error = str(err)
            return
        return self.parse(html)

    def parse(self, html):
        """ """
        if isinstance(html, BeautifulSoup):
            doc = html
        else:
            doc = BeautifulSoup(html, "html.parser")
        try:
            ogs = doc.html.head.findAll(property=re.compile(r"^og"))
        except:
            self.error = "Parsing Error: Open Graph Meta Not Found"
            ogs = []
        for og in ogs:
            if og.has_attr("content"):
                self[og["property"][3:]] = og["content"]
        # Couldn't fetch all attrs from og tags, try scraping body
        if not self.is_valid() and self.scrape:
            for attr in self.required_attrs:
                if not self.valid_attr(attr):
                    try:
                        self[attr] = getattr(self, "scrape_%s" % attr)(doc)
                    except AttributeError:
                        pass

    def valid_attr(self, attr):
        return self.get(attr) and len(self[attr]) > 0

    def is_valid(self):
        return all([self.valid_attr(attr) for attr in self.required_attrs])

    def to_html(self):
        if not self.is_valid():
            return '<meta property="og:error" content="og metadata is not valid" />'

        meta = ""
        for key, value in self.iteritems():
            meta += '\n<meta property="og:%s" content="%s" />' % (key, value)
        meta += "\n"

        return meta

    def to_json(self):
        if not self.is_valid():
            return json.dumps({"error": "og metadata is not valid"})

        return json.dumps(self)

    def to_xml(self):
        pass

    def scrape_image(self, doc):
        image = ""
        images = [dict(img.attrs)["src"] for img in doc.html.body.findAll("img")]
        if images:
            image = images[0]
            image_url = urlparse(image)
            if not image_url.netloc:
                image = urlopen(self.url).geturl().strip("/") + image
        return image

    def scrape_title(self, doc):
        try:
            return doc.html.head.title.text
        except:
            return ""

    def scrape_type(self, _):
        return "other"

    def scrape_url(self, _):
        return self.url

    def scrape_description(self, doc):
        try:
            tag = doc.html.head.findAll("meta", attrs={"name": "description"})
            result = "".join([t["content"] for t in tag])
            return result
        except:
            return ""
