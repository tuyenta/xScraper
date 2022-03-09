"""
Copyright 2021 @Duc Tuyen TA

"""
import os
import logging
from bs4 import BeautifulSoup as soup

logger = logging.getLogger(__name__)


class GoogleResult:
    """
    Simple class that will take contents of a <div class="g">
    """

    def __init__(self, div_g):
        self.div_g = div_g

    def get_title(self):
        """
        Return the title of the search
        using <h3> to determine this
        """

        title = self.div_g.find_all("h3")
        try:
            title = title[0].text
        except IndexError:
            logger.warning("could not get title of search")
            title = None
        return title

    def get_links(self):
        """
        Return a list of links contained within the results
        Probably want to filter so we only get pdfs
        """

        links = self.div_g.find_all("a", href=True)
        return links

    @property
    def title(self):
        return self.get_title()

    @property
    def primary_link(self):
        """
        There can be multiple links in a search results.
        e.g. to cached values etc.
        Want to make sure we only get the primary link
        """

        links = []
        for link in self.get_links():
            # ignore cached results as they may double up results
            if "webcache" in link["href"].lower():
                continue
            if link.text == "Similar":
                # skip similar links, they go to other searchers
                continue
            if "http" not in link["href"].lower():
                continue
            # need to filter out query string for downloading
            qindx = link["href"].find("?")
            if qindx > 0:
                links.append(link["href"][0:qindx])
            else:
                links.append(link["href"])
        if links:
            return links[0]

    @property
    def do_download(self):
        """
        Bool to determine if we should attempt to download the file
        currently just on pdf but could change it to other file types

        returns: bool
        """

        dl = False
        if os.path.basename(self.primary_link).lower().endswith(".pdf"):
            dl = True
        return dl


def get_search_results(webpage):
    """
    Break down the search into indiviual items
    using <div class="g"

    Later on we will extract title and links from
    these results
    """

    soup_page = soup(webpage, "html.parser")
    results = soup_page.find_all("div", {"class": "g"})
    logger.info(f"Found {len(results)} results, processing now")
    for result in results:
        googleresult = GoogleResult(result)
        if googleresult.title is not None:
            # no title is a People also Ask or Related Search, we ignore these
            yield googleresult
