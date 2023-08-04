from transaction_scraper import Transactions
import time
import sys

# TODO copy user data profile folder so cookies can be reused

# get data from mercado pago
# first arg = binary path
binPath = sys.argv[1]

# second arg = page link
link = sys.argv[2]

driver = Transactions(binPath)

driver.goTo(link)
time.sleep(3)

data = driver.scrapeData()
links = driver.scrapeLinks()

for entry in data:
    print("nome: " + entry['name'] + " | ")
    print("data: " + entry['time'] + "\n")

for link in links:
    print(link)
