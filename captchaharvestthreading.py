import threading
from bs4 import BeautifulSoup
import re
import pandas as pd
import os
from collections import OrderedDict as OrderedDict
import requests
import time
import sys
from python3_anticaptcha import NoCaptchaTaskProxyless
import mysql.connector
import datetime as dt
import ctypes

ctypes.windll.kernel32.SetConsoleTitleW("Captchaharvest RRR")

# Database configuration
DB_CONFIG = {
    "host": "34.70.96.52",
    "user": "order",
    "passwd": "acceptance",
    "database": "capcha_harvest"
}

# Anti-captcha configuration
ANTICAPTCHA_KEY = '93c6bd2f995793509ae16302184279dc'
SITE_KEY = '6Lermf0SAAAAAK4CoF1Ep6U1fEj7ukaBx3txV-hc'
PAGE_URL = 'https://legacy.rrreview.com/home.aspx'

def harvest_captcha():
    while True:
        print('Captcha Harvesting running....')
        try:
            print("Harvesting Captcha...")
            user_answer = NoCaptchaTaskProxyless.NoCaptchaTaskProxyless(anticaptcha_key=ANTICAPTCHA_KEY)\
                .captcha_handler(websiteURL=PAGE_URL, websiteKey=SITE_KEY)
            grecaptchakey = user_answer['solution']['gRecaptchaResponse']
            print(grecaptchakey)

            # Connect to the database
            mydb = mysql.connector.connect(**DB_CONFIG)
            mycursor = mydb.cursor()

            # Insert the captcha token into the database
            addtokenquery = ("INSERT INTO tokens (id, ctoken) VALUES (%s, %s)")
            ctoken = ('', grecaptchakey)
            mycursor.execute(addtokenquery, ctoken)
            mydb.commit()
            print(mycursor.rowcount, "Token inserted.")

            # Close the database connection
            mycursor.close()
            mydb.close()

            # Wait before the next iteration (optional)
            # time.sleep(60)  # Adjust the sleep time as needed

        except Exception as ex:
            print(ex)
            # Optional: Sleep for a while before retrying in case of an error
            time.sleep(10)

def main():
    # Create a list to hold threads
    threads = []

    # Number of threads you want to run
    num_threads = 5

    for i in range(num_threads):
        thread = threading.Thread(target=harvest_captcha)
        thread.start()
        threads.append(thread)

    # Join threads to wait for their completion
    for thread in threads:
        thread.join()

if __name__ == "__main__":
    main()
