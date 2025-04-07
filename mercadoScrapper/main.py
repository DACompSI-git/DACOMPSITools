from transaction_scraper import Transactions
import time
import xlsxwriter
import os.path
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
timeCol = 2
amountCol = 3
linkCol = 4
row = 0

# third arg forward = html pages to get data from
linkFolder = sys.argv[3]

driver = Transactions(binPath)

# initial page number
pageNum = 1

while True:
    filePath = linkFolder + "/" + str(pageNum).zfill(2) + ".html"

    if (not os.path.isfile(filePath)):
        print("Path " + filePath + " doesn't exist")
        break

    link = "file://" + filePath
    driver.goTo(link)
    #time.sleep(3)

    data = driver.scrapeData()

    for entry in data:
        #print("nome: " + entry['name'] + " | ")
        worksheet.write(row, nameCol, entry['name'])
        #print("data: " + entry['time'] + " | ")
        worksheet.write(row, dateCol, entry['date'])
        worksheet.write(row, timeCol, entry['time'])
        #print("quantidade: " + "{:.2f}".format(entry['amount']) + " | ")
        worksheet.write(row, amountCol, "{:.2f}".format(entry['amount']))
        #print("link: " + entry['link'] + "\n")
        worksheet.write(row, linkCol, entry['link'])
        row += 1

    pageNum = pageNum + 1

driver.close()
workbook.close()
