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

# start_hour = 6
# end_hour = 4

while True:
        # if start_hour <= dt.datetime.now().hour and end_hour >= dt.datetime.now().hour:
        print('Captcha Harvesting running....')
        try:
                print("Harvesting Captcha...")
                ANTICAPTCHA_KEY = '93c6bd2f995793509ae16302184279dc'
                SITE_KEY = '6Lermf0SAAAAAK4CoF1Ep6U1fEj7ukaBx3txV-hc'
                PAGE_URL = 'https://legacy.rrreview.com/home.aspx'
                user_answer = NoCaptchaTaskProxyless.NoCaptchaTaskProxyless(anticaptcha_key = ANTICAPTCHA_KEY)\
                                                                                .captcha_handler(websiteURL=PAGE_URL,
                                                                                                websiteKey=SITE_KEY)
                grecaptchakey = user_answer['solution']['gRecaptchaResponse']
                print(grecaptchakey)
                mydb = mysql.connector.connect(
                        host="34.70.96.52",
                        user="order",
                        passwd="acceptance",
                        database="capcha_harvest"
                        )
                mycursor = mydb.cursor()
                addtokenquery = ("INSERT INTO tokens "
                        "(id,ctoken) "
                        "VALUES (%s,%s)")
                ctoken=('',grecaptchakey)
                mycursor.execute(addtokenquery,ctoken)
                mydb.commit()
                print(mycursor.rowcount, "Token inserted.")

        except Exception as ex:
                print(ex)
