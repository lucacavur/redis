import redis
import requests
from bs4 import BeautifulSoup
import pymongo as mongo

#mongo
myclient = mongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["BitcoinScraper"]
mycol = mydb["BitcoinScraper"]

#redis
r = redis.Redis(host="localhost", port=6379)

#create a list to store values
rawValues = []

#create a current-time variable to make it real-time
currentTime = ""

#creata variable for most valuable BTC
biggestBTC = 0

#url
url = "https://www.blockchain.com/btc/unconfirmed-transactions"

while True:
    #scrape the page 
    r = requests.get(url)
    soup = BeautifulSoup(r.text, features="html.parser")
    variables = soup.find_all('div', {'class':'sc-1g6z4xm-0 hXyplo'})

    #clean and append to list
    for variable in variables:
        value = variable.text
        value = value.replace("Hash", "")
        value = value.replace("Time", " ")
        value = value.replace("Amount", "")
        value = value.replace("(USD)", "")
        value = value.replace("(BTC)", "")
        value = value.replace("BTC", "")
        value = value.split(" ")
        rawValues.append(value)

    #current time
    if currentTime=="":
        currentTime = value[1]
    
    #biggest hash
    for value in rawValues:
        #if times are equal
        if currentTime == value[1]:
            #create redis dictionary
            hash = value[0]
            time = value[1]
            btc = value[2]
            usd = value[3]

            dict = {"Time": time, "Hash":hash, "BTC_Value":btc, "USD_Value":usd}
            r.lpush("Data",str(dict))

            #find the 4  top-variables
            if float(value[2])>float(biggestBTC):
                biggestBTC = float(value[2])
                biggestTime = value[1]
                biggestHash = value[0]
                biggestUSD = value[4]
            
        #if time is bigger than currentTime
        if value[1]>currentTime:

            #mongo
            mydict = { "Time": biggestTime, "Hash": biggestHash, "BTC Value": biggestBTC, "USD Value": biggestUSD}
            x = mycol.insert_one(mydict)
            x.inserted_id
            
            #delete all redis keys
            r.flushall()
            
            #clear all variables and the list, adapt the current time    
            rawValues=[]
            dict = {}
            currentTime = value[1]
            biggestBTC = 0