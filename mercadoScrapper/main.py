from transaction_scraper import Transactions
import time
import xlsxwriter
import sys

# TODO copy user data profile folder so cookies can be reused

# get data from mercado pago
# first arg = binary path
binPath = sys.argv[1]

# second arg = page link
xlsxFileName = sys.argv[2]
workbook = xlsxwriter.Workbook(xlsxFileName)
worksheet = workbook.add_worksheet()

nameCol = 0
dateCol = 1
amountCol = 2
linkCol = 3
row = 0

# third arg forward = html pages to get data from
links = sys.argv[3:]

driver = Transactions(binPath)

for link in links:
    driver.goTo(link)
    #time.sleep(3)

    data = driver.scrapeData()

    for entry in data:
        #print("nome: " + entry['name'] + " | ")
        worksheet.write(row, nameCol, entry['name'])
        #print("data: " + entry['time'] + " | ")
        worksheet.write(row, dateCol, entry['time'])
        #print("quantidade: " + "{:.2f}".format(entry['amount']) + " | ")
        worksheet.write(row, amountCol, "{:.2f}".format(entry['amount']))
        #print("link: " + entry['link'] + "\n")
        worksheet.write(row, linkCol, entry['link'])
        row += 1

driver.close()
workbook.close()
