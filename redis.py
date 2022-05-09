import requests
from bs4 import BeautifulSoup
import time
import pymongo as mongo 
import redis

def scrape():
    #scrape the page 
    url = "https://www.blockchain.com/btc/unconfirmed-transactions"
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")

    #get the variables
    variables = soup.find_all('div', {'class':'sc-6nt7oh-0 PtIAf'})

    #put variables in a list
    rawValues = []
    for variable in variables:
        rawValues.append(variable.text)

    #put in another list, without commas
    cleanValues = []
    for value in rawValues:
        value = value.replace(",", "")
        cleanValues.append(value)

    #find the most valued USDValue, filter out "$" 
    USDvalues = []
    for value in cleanValues:
        if value[0] == '$':
            value = value.replace("$", "")
            USDvalues.append(float(value))

    USDvalues.sort(reverse=True)
    highest = round(USDvalues[0], 2)
    highest_USDvalue = "$"+str(highest)

    #find the index of the highest_USDvalue within the clean values
    index = -1
    for value in cleanValues:
        index+=1
        if value == highest_USDvalue:
            break

    #find the other values
    hashValue = cleanValues[index-3]
    timeValue = cleanValues[index-2]
    BTCValue = cleanValues[index-1]

    #mongo
    #myclient = mongo.MongoClient("mongodb://localhost:27017/")
    #mydb = myclient["BitcoinScraper"]
    #mycol = mydb["BitcoinScraper"]

    #mydict = { "Time": timeValue, "Hash": hashValue, "BTC Value": BTCValue, "USD Value": highest_USDvalue}

    #x = mycol.insert_one(mydict)

    #redis
    r = redis.Redis()
    r.mset({"Time":timeValue, "Hash":hashValue, "BTC value":BTCValue, "USD value":highest_USDvalue})
    r.get("USD Value")

while True:
    scrape()
    #scrape every 4 seconds
    time.sleep(4)