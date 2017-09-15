#!/usr/bin/env python3
""" Module to scrap ads from the OLX website. """

from contextlib import contextmanager
from selenium import webdriver


class OlxAd():
    """ Represents an ad from the OLX website. """
    def __init__(self, olx_id, name, link, price):
        self.olx_id = olx_id
        self.name = name
        self.link = link
        self.price = price


@contextmanager
def _open_webdriver(driver_type=webdriver.PhantomJS):
    """ Context manager for the webdriver.

        Arguments:
            driver_type -- class reference for the webdriver
                           to be used (default: selenium.webdriver.PhantomJS)

        Returns:
            A context manager for the webdriver.
    """
    driver = driver_type()
    try:
        yield driver
    finally:
        driver.quit()


def _get_urls(path='url.txt'):
    """ Returns URLs from the file used by the main function.

        Arguments:
            path -- path to the URL file (default: 'url.txt')

        Returns:
            A generator for the URLs contained in the file.
    """
    with open(path, mode='r') as file:
        for row in file:
            yield row


def _get_result_pages(driver, url):
    """ Return pages from the result of a search on the OLX website.

        Arguments:
            driver -- the driver being utilized in the scrapper
            url -- URL of the search to be made

        Returns:
            A generator to redirect the driver to the next result page.
    """
    driver.get(url)

    if driver.find_elements_by_class_name('section_not_found'):
        raise StopIteration() # zero results

    yield driver

    pag_elem = driver.find_element_by_class_name('module_pagination')
    if not pag_elem:
        raise StopIteration() # one page result

    next_elems = pag_elem.find_elements_by_class_name('next')
    while next_elems:
        next_url = next_elems[0].find_element_by_class_name('link').get_attribute('href')
        driver.get(next_url)
        yield driver
        pag_elem = driver.find_element_by_class_name('module_pagination')
        next_elems = pag_elem.find_elements_by_class_name('next')


def _get_ads_from_page(driver):
    """ Return the ads from a result page.

        Arguments:
            driver -- the driver being utilized in the scrapper

        Returns:
            A generator that returns the ads from the page.
    """
    list_elem = driver.find_element_by_id('main-ad-list')
    for item in list_elem.find_elements_by_class_name('item'):
        if 'list_native' not in item.get_attribute('class'):
            link_elem = item.find_element_by_class_name('OLXad-list-link')

            olx_id = link_elem.get_attribute('id')
            link = link_elem.get_attribute('href')
            name = link_elem.get_attribute('title')

            price_elems = item.find_elements_by_class_name('OLXad-list-price')
            if price_elems:
                price = price_elems[0].text
            else:
                price = None

            olx_ad = OlxAd(olx_id, name, link, price)
            yield olx_ad


def _get_ads_from_url(driver, url):
    """ Get all ads from a URL from the OLX website.

        Arguments:
            driver -- the webdriver to be used for the search
            url -- url to be scrapped

        Returns:
            A generator that returns the ads.
    """
    for page in _get_result_pages(driver, url):
        for olx_ad in _get_ads_from_page(page):
            yield olx_ad


def _print_ads(olx_ads):
    """ Print a iterator of OlxAds into the screen.

        Arguments:
            olx_ads -- iterator of ads to print
    """
    for olx_ad in olx_ads:
        print(f'{olx_ad.olx_id} -- {olx_ad.name} -- {olx_ad.price}')


def main():
    """ Search all the URLs in the 'url.txt' file and save the result
        in the 'result.csv' file.
    """
    with open('result.csv', mode='w') as file:
        file.write('url;olx_id;name;price;link\n')
        with _open_webdriver() as driver:
            for url in _get_urls():
                for olx_ad in _get_ads_from_url(driver, url):
                    print(f'{olx_ad.olx_id} -- {olx_ad.name} -- {olx_ad.price}')
                    file.write(f'{url};{olx_ad.olx_id};{olx_ad.name};{olx_ad.price};{olx_ad.link}\n')


if __name__ == '__main__':
    main()
