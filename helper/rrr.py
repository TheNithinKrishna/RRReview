import logging
import re
from scrapy.http import HtmlResponse
from bs4 import BeautifulSoup
import datetime
import email
import requests
import time
import json
import mysql.connector
import urllib.parse
from email import policy
from urllib.parse import unquote
from requests.cookies import RequestsCookieJar

from stdlib.utility import cursorexec,ignored_order,check_ordertype,criteria_with_params,login_into_gmail,exception_mail_send,send_accepted_mail,write_to_db

class RRReview:
    def __init__(self,client_data) -> None:
        self.client_data=client_data
        
    def criteria_check(self,order_details,portal_name):     #Function to check criteria of an order
        try:
            common_db_data=cursorexec("order_updation",'SELECT',"""SELECT * FROM `common_data_acceptance` """)
            from datetime import datetime as dt
            from pytz import timezone
            due_date=order_details['order_due'].split(" ")[0]
            date_obj = dt.strptime(due_date, '%m/%d/%Y')
            dts=dt.strftime(date_obj, '%m/%d/%Y')
            logging.info(dts)
            zone = timezone('EST')
            today=dt.strftime(dt.now(zone), '%m/%d/%Y')
            logging.info(today)
            d1 = dt.strptime(today, "%m/%d/%Y")
            d2 = dt.strptime(dts, "%m/%d/%Y")
            due_difference=((d2 - d1).days)
            price_in_db,zipcode_in_db,ordertype_flag=check_ordertype(order_details['order_type'],order_details['order_fee'],common_db_data,self.client_data,portal_name)
            if ordertype_flag:
                zipcode_in_db={zipcode: True for zipcode in zipcode_in_db.split(',')}
                ignore_msg,fee,criteria_flag=criteria_with_params(price_in_db,zipcode_in_db, order_details['order_fee'],due_difference,order_details['order_zip'],self.client_data,order_details['order_due'],common_db_data,portal_name)
                return ignore_msg,criteria_flag
            else:
                return "Order Type Not Satisfied",ordertype_flag
        except Exception as ex:
            logging.info(ex)
            exception_mail_send(portal_name,"RRR-Criteria check function ",ex)
            
    def captcha_solving(self):                              #Fucntion used to fetch captcha tokens from the database
        try:
            import datetime
            datetime.datetime.now()
            logging.info("Capturing Token from DB")
            mydb = mysql.connector.connect(
                        host="34.70.96.52",
                        user="order",
                        passwd="acceptance",
                        database="capcha_harvest"
                        )
            mycursor = mydb.cursor()
            getquery = ("select * from tokens where time >= DATE_SUB(NOW(), INTERVAL 90 SECOND) order by time asc limit 1")
            mycursor.execute(getquery)
            data = mycursor.fetchone()
            logging.info(data)
            sql = "DELETE  FROM  tokens WHERE id = '{}'".format(data[0])
            mycursor.execute(sql)
            mydb.commit()
            return data[1]
        except Exception as ex:
            logging.info(ex)
            exception_mail_send("RRReview","RRReview-captcha_solving function ",ex)   
        
    def accept_order(self,session,pageurl,orderid,soup):        #Function to accept an order          
        retry_attempts = 2
        attempt = 0
        while attempt < retry_attempts:    
            try:
                # logging.info(soup.text)
                # cookie_value = session.cookies.get('ASP.NET_SessionId')
                # value = 'ASP.NET_SessionId={}'.format(cookie_value)
                logging.info("Parameters Scraping...")
                view_state = soup.find('input', {'id': '__VIEWSTATE'}).get('value')
                view_state_generator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
                view_state_event_validation = soup.find('input', {'id': '__EVENTVALIDATION'}).get('value')
                logging.info("Required Data Scrapped!!")
                grecaptchakey=self.captcha_solving()
                logging.info("Captcha key: {}".format(grecaptchakey))
                # json_string = json.dumps({"text":"Submit","value":"","checked":False,"target":"","navigateUrl":"","commandName":"","commandArgument":"","autoPostBack":True,"selectedToggleStateIndex":0,"validationGroup":None,"readOnly":False,"primary":False,"enabled":False})
                data1={
                    'scriptManager_HiddenField': '',
                    '__EVENTTARGET': 'ctl00$Main$buttonAccept',
                    '__EVENTARGUMENT': '',
                    '__LASTFOCUS': '',
                    '__VIEWSTATE': view_state,
                    'ctl00$Main$acceptDecline': 'buttonAccept',
                    # 'ctl00_Main_btnSubmit_ClientState':json_string,
                    '__VIEWSTATEGENERATOR': view_state_generator,
                    '__EVENTVALIDATION': view_state_event_validation
                    }
                response1 = session.post(pageurl, data=data1,headers=self.get_headers({'Referer': pageurl})) #, 'Cookie':value})) #
                soup = BeautifulSoup(response1.content, 'html.parser')
                view_state = soup.find('input', {'id': '__VIEWSTATE'}).get('value','')
                view_state_generator = soup.find('input', {'id': '__VIEWSTATEGENERATOR'}).get('value')
                view_state_event_validation = soup.find('input', {'id': '__EVENTVALIDATION'}).get('value')
                # json_string =json.dumps({"text":"Submit","value":"","checked":False,"target":"","navigateUrl":"","commandName":"","commandArgument":"","autoPostBack":True,"selectedToggleStateIndex":0,"validationGroup":None,"readOnly":False,"primary":False,"enabled":True})
                data2 = {
                            'ctl00$Main$scriptManager': 'ctl00$Main$updatePanelPage|ctl00$Main$btnSubmit',
                            'scriptManager_HiddenField': '',
                            '__EVENTTARGET': '',
                            '__EVENTARGUMENT': '',
                            '__LASTFOCUS': '',
                            '__VIEWSTATE': view_state,
                            '__VIEWSTATEGENERATOR': view_state_generator,
                            '__EVENTVALIDATION': view_state_event_validation,
                            'ctl00$Main$acceptDecline': 'buttonAccept',
                            'g-recaptcha-response': grecaptchakey,
                            # 'ctl00_Main_btnSubmit_ClientState': json_string,
                            '__ASYNCPOST': 'true',
                            'ctl00$Main$btnSubmit': 'Submit'
                }
                logging.info(f"data2:{data2}")
                logging.info("Captcha Solved")
                headers={
                        'Accept': '*/*',
                        'Accept-Encoding': 'gzip, deflate, br, zstd',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Cache-Control': 'no-cache',
                        'Connection': 'keep-alive',
                        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                        # 'Cookie': value,
                        'Host': 'legacy.rrreview.com',
                        'Origin': 'https://legacy.rrreview.com',
                        'Referer': pageurl,
                        'Sec-Fetch-Dest': 'empty',
                        'Sec-Fetch-Mode': 'cors',
                        'Sec-Fetch-Site': 'same-origin',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
                        'X-MicrosoftAjax': 'Delta=true',
                        'X-Requested-With': 'XMLHttpRequest',
                        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"'													
                        }
                response = session.post(pageurl, data=data2,headers=headers)                
                soup = BeautifulSoup(response.content, 'html.parser')
                logging.info(soup.text)
                    
                if 'Thank you for accepting this order!' in soup.text and orderid in soup.text:
                    logging.info("Order Accepted Succesfully")
                    accept_flag='True'
                    return accept_flag
                elif 'Unfortunately, this order is no longer available.' in soup.text:
                    logging.info("Order Expired")
                    accept_flag='Order Expired'
                    return accept_flag
                else:
                    logging.info("Captcha issue")
                    if attempt < retry_attempts - 1:
                        logging.info("Retrying captcha solution...")
                    attempt += 1    
                    # return False
            except Exception as ex:
                logging.info(ex)
                exception_mail_send("RRReview","RRReview-accept_order function ",ex)       
        logging.info("Failed to accept the order after retrying.")
        return False
    def get_headers(self,additonal_headers):        #Function to fetch the common headers used in acceptance
        try:
            # cookie_jar = RequestsCookieJar()
            # cookie_value = cookie_jar.get('ASP.NET_SessionId')
            # value = ''
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Accept-Encoding': 'gzip, deflate, br, zstd',
                'Accept-Language': 'en-US,en;q=0.9',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                # 'Cookie': 
                'Host': 'legacy.rrreview.com',
                'Origin': 'https://legacy.rrreview.com',
                'Referer': "pageurl",
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-User': '?1',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',


                															
                }
            if len(additonal_headers)> 0 :
                for a_head in additonal_headers: headers[a_head] = additonal_headers[a_head]
            return headers
        except Exception as ex:
            logging.info(ex)   
    def fetch_details_mail(self,GMAIL_USERNAME,GMAIL_PASSWORD,portal_name):     #Fucntion to fetch details from the email notification
        try:
            conn = login_into_gmail(GMAIL_USERNAME, GMAIL_PASSWORD)
            conn.select('Inbox')
            retcode, messages = conn.search(None, '(SUBJECT "New Order Available" UNSEEN)')
            str_list = list(filter(None, messages[0].decode().split(' ')))
            from datetime import datetime
            cursorexec("order_updation",'UPDATE',f"""UPDATE `servercheck` SET `event`='{datetime.now()}' where `id`='315' """)
            if retcode == 'OK':
                for num in messages[0].decode().split(' '):
                    if num!='':
                        # print('New order Found!!!')
                        logging.info('New order Found!!!')
                        typ, data = conn.fetch(num,'(RFC822)')
                        for response_part in data:
                            if isinstance(response_part, tuple):
                                msg = email.message_from_bytes(response_part[1], policy=policy.default)
                                client_mail=msg['To']
                                subject=msg['Subject']
                                logging.info(client_mail)
                                logging.info(subject)
                                if msg.get_content_type()=='text/html':
                                    y = msg.get_payload(decode=True)
                                    body_repsonse = HtmlResponse(url="my HTML string", body=y, encoding='utf-8')
                                elif msg.get_content_type()=='multipart/mixed':
                                    for x in msg.get_payload():
                                        if x.get_content_type()=='text/html':
                                            y = x.get_payload(decode=True)
                                            body_repsonse = HtmlResponse(url="my HTML string", body=y, encoding='utf-8')        
                                else:
                                    # print(msg.get_content_type())
                                    # print('content type')
                                    logging.info(msg.get_content_type())
                                    logging.info('content type')             
            
                            accept_link=body_repsonse.xpath("//a/@href").extract_first()
                            pattern = r"""GUID=(.*?)&."""
                            match =  re.findall(pattern,str(accept_link), re.DOTALL)
                            if match:guid = match[0].replace('=', '').replace(r"\r\n", r"")
                            ord_id=body_repsonse.xpath('//strong//span[contains(text(),"ORDER #:")]//following::span//span//text()').extract_first()
                            ord_type=body_repsonse.xpath('//strong//span[contains(text(),"INSPECTION:")]//following::span//span//text()').extract_first()
                            ord_due=body_repsonse.xpath('//td//p//b//span[contains(text(),"DUE DATE:")]//following::td//p//span//span//font//strong//span//text()').extract_first()
                            ord_fee=body_repsonse.xpath('//td//p//b//span[contains(text(),"FEE:")]//following::td//p//span[2]//font//text()').extract_first()
                            ord_fee=ord_fee.split('.')[0]
                            ord_address=body_repsonse.xpath('//td//p//b//span[contains(text(),"ADDRESS:")]//following::td//p//span//font//text()').extract_first()
                            ord_address=ord_address.replace('\r','').replace('\n','')
                            ord_address=re.sub(r'\s+',' ',ord_address)
                            ord_zip=ord_address.split()[-1]
                            print(ord_type,ord_fee,ord_address,ord_zip,ord_id)
                            order_details=[]
                            order_details.append({'order_type':ord_type,'order_fee':ord_fee,"order_address":ord_address,"order_zip":ord_zip,"order_due":ord_due,"order_id":ord_id,"order_accept_link":accept_link,"order_guid":guid,"client_mail":client_mail})
                            return order_details,subject
                    else:
                        logging.info(f"No New Messages {portal_name}")
                        subject='No Orders'
                        return "No Orders",subject
        except Exception as ex:
                # print(ex)
                logging.info(ex)
            
    def process_order(self, session, order_details, client_data, soup,subjectline):
        accept_flag = self.accept_order(session,order_details['order_accept_link'], order_details['order_id'], soup)
        if accept_flag=='True':
            if 'EXCLUSIVE' in subjectline:
                mail_status = send_accepted_mail(order_details['order_due'], order_details['order_fee'], order_details['order_type'], order_details['order_address'], order_details['order_id'], client_data['from_mail'], client_data['to_clientMail'], client_data['to_ecesisMail'], client_data['Client_name'], "Exclusive RRReview order Accepted!", "RRReview")
                write_to_db(client_data, datetime.datetime.now(), order_details['order_due'], "RRReview", order_details['order_fee'], order_details['order_type'], order_details['order_address'], mail_status, "RRReview", order_details['order_id'],"Exclusive RRReview order Accepted!",order_details['order_received_time'])
            else:
                mail_status = send_accepted_mail(order_details['order_due'], order_details['order_fee'], order_details['order_type'], order_details['order_address'], order_details['order_id'], client_data['from_mail'], client_data['to_clientMail'], client_data['to_ecesisMail'], client_data['Client_name'], "RRReview order Accepted!", "RRReview")
                write_to_db(client_data, datetime.datetime.now(), order_details['order_due'], "RRReview", order_details['order_fee'], order_details['order_type'], order_details['order_address'], mail_status, "RRReview", order_details['order_id'],"RRReview order Accepted!",order_details['order_received_time'])
        elif accept_flag=='Order Expired': 
            if 'EXCLUSIVE' in subjectline:
                subjectline = 'Exclusive'
                subject="Ignored Exclusive Order!!! - RRR-"
                ignored_msg = "Order Expired"
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)    
            else:
                subjectline = 'Broadcasted'
                subject="Ignored Order!!! - RRR-"
                ignored_msg = "Order Expired"
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)
        else:
            if 'EXCLUSIVE' in subjectline:
                subjectline = 'Exclusive'
                subject="Ignored Exclusive Order!!! - RRR-"
                ignored_msg = "Captcha issue"
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)    
            else:
                subjectline = 'Broadcasted' 
                subject="Ignored Order!!! - RRR-"
                ignored_msg = "Captcha issue"
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)  
                