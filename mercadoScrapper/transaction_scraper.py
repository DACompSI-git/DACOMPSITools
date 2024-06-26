from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

import requests
import re

class Transactions:
    def __init__(self, binary):
        chromeOptions = webdriver.ChromeOptions()
        if binary:
            chromeOptions.binary_location = binary

        # enable selenium to run before page is fully loaded
        chromeOptions.page_load_strategy = 'eager'

        self.browser = webdriver.Chrome(chromeOptions)

    def close(self):
        self.browser.quit()

    # go to a specific URL
    def goTo(self, url):
        if self.browser:
            self.browser.get(url)

            # stop page loading, preventing it from being cleaned due to nonexistant cookies
            self.browser.execute_script("window.stop();")

    # find list of li elements containing transaction data.
    def findList(self):
        # narrow up elements for better speed
        acList = self.browser.find_element(By.CLASS_NAME, "c-activity-list")
        ulList = acList.find_element(By.TAG_NAME, "ul")
        return ulList.find_elements(By.TAG_NAME, "li")

    # get name from transaction li element.
    def getTransactionName(self, li):
        try:
            div = li.find_element(By.CLASS_NAME, "ui-action-row__description")
            span = div.find_element(By.TAG_NAME, "span")
            # remove redundant leading transaction designators
            return re.sub("^de |^para ", "", span.text)

        except NoSuchElementException as nf:
            # return empty name since it doesn't exist
            return ""

    # get date from transaction li element.
    def getTransactionDate(self, li):
        time = li.find_element(By.TAG_NAME, "time")
        return time.text

    # get link to transaction from transaction li element.
    def getTransactionLink(self, li):
        link = li.find_element(By.TAG_NAME, "a").get_attribute('href')
        return link

    # get amount transferred in transaction.
    def getTransactionAmount(self, li):
        outerSpan = li.find_element(By.CLASS_NAME, "andes-money-amount")
        fractionDiv = outerSpan.find_element(By.CLASS_NAME, "andes-money-amount__fraction")
        centsDiv = outerSpan.find_element(By.CLASS_NAME, "andes-money-amount__cents")

        fractionAmount = int(fractionDiv.text.replace('.','')) * 100
        centsAmount = int(centsDiv.text)

        # check if it's outgoing transaction
        multiplier = 1
        try:
            negativeDiv = outerSpan.find_element(By.CLASS_NAME, "andes-money-amount__negative-symbol")
            multiplier = -1
        except NoSuchElementException:
            multiplier = 1

        return ((fractionAmount + centsAmount) / 100) * multiplier

    # scrape links from transactions, returning a list of links.
    def scrapeLinks(self):
        if not self.browser:
            return []

        links = []

        try:
            fullList = self.findList();

            for li in fullList:
                # get links
                link = li.find_element(By.TAG_NAME, "a").get_attribute('href')
                links.append(link)

        except NoSuchElementException as nf:
            # element not found; inform user
            print("Não foi possível encontrar o elemento informado pelo selenium: \n" + nf.msg)

        except StaleElementReferenceException as se:
            # element not found; inform user
            print("A página mudou e o elemento não pode mais ser acessado: \n" + se.msg)
            print("Stack trace: " + se.stacktrace)

        return links

    # scrape data from transactions, returning a list of transaction infos.
    def scrapeData(self):
        if not self.browser:
            return []

        data = []

        try:
            fullList = self.findList();

            for li in fullList:
                # get direct info
                info = {}
                name = self.getTransactionName(li)
                time = self.getTransactionDate(li)
                link = self.getTransactionLink(li)
                amount = self.getTransactionAmount(li)

                info['name'] = name
                info['time'] = time
                info['link'] = link
                info['amount'] = amount
                data.append(info)

        except NoSuchElementException as nf:
            # element not found; inform user
            print("Não foi possível encontrar o elemento informado pelo selenium: \n" + nf.msg)

        except StaleElementReferenceException as se:
            # element not found; inform user
            print("A página mudou e o elemento não pode mais ser acessado: \n" + se.msg)
            print("Stack trace: " + se.stacktrace)

        data.reverse()

        return data
