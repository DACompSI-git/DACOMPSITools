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

    # find groups of lists of li elements containing transaction data.
    def findList(self):
        # narrow up elements for better speed
        acList = self.browser.find_element(By.CLASS_NAME, "andes-list")
        #ulList = acList.find_element(By.TAG_NAME, "ul")
        return acList.find_elements(By.CLASS_NAME, "binnacle-rows-wrapper")

    def findTransactionGroups(self, li):
        ol = li.find_element(By.TAG_NAME, "ol")
        return ol.find_elements(By.TAG_NAME, "li")

    # get name from transaction li element.
    def getTransactionName(self, li):
        col = li.find_element(By.CLASS_NAME, "andes-list__item-first-column")
        try:
            span = col.find_element(By.CLASS_NAME, "andes-list__item-secondary")
            return span.text

        except NoSuchElementException:
            # get primary column since it always exists
            span = col.find_element(By.CLASS_NAME, "andes-list__item-primary")
            return span.find_element(By.CLASS_NAME, "binnacle-row__title").text

    # get group date from li element.
    def getTransactionDate(self, li):
        try:
            div = li.find_element(By.CLASS_NAME, "binnacle-rows-wrapper__title")
            return div.text

        except NoSuchElementException as nf:
            # return empty name since it doesn't exist
            return "BADDATE"

    def getTransactionTime(self, li):
        column = li.find_element(By.CLASS_NAME, "andes-list__item-second-column")
        time = column.find_element(By.CLASS_NAME, "binnacle-row__time")
        return time.text.replace('h',':')


    # get link to transaction from transaction li element.
    def getTransactionLink(self, li):
        link = li.find_element(By.TAG_NAME, "a").get_attribute('href')
        return link

    # get amount transferred in transaction.
    def getTransactionAmount(self, li):
        column = li.find_element(By.CLASS_NAME, "andes-list__item-second-column")
        outerSpan = column.find_element(By.CLASS_NAME, "andes-money-amount")
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
            group = self.findList()
            for li in group:
                date = self.getTransactionDate(li)
                groupTransactions = self.findTransactionGroups(li)
                for tran in groupTransactions:
                    info = {}
                    name = self.getTransactionName(tran)
                    time = self.getTransactionTime(tran)
                    link = self.getTransactionLink(tran)
                    amount = self.getTransactionAmount(tran)
                    info['name'] = name
                    info['date'] = date
                    info['time'] = time
                    info['amount'] = amount
                    info['link'] = link
                    data.append(info)

        except NoSuchElementException as nf:
            # element not found; inform user
            print(f"Não foi possível encontrar o elemento informado pelo selenium: ${nf.msg}")

        except StaleElementReferenceException as se:
            # element not found; inform user
            print(f"A página mudou e o elemento não pode mais ser acessado: ${se.msg}")
            print(f"Stack trace: ${se.stacktrace}")

        data.reverse()

        return data
