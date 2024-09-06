"""FILE CONTAINS THE RRReview MAIN FUNCTION which is used to run the acceptance"""
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import sys
import logging
import threading
from stdlib.utility import cursorexec,checkip,inactive_inDB,logger_mail,ignored_order,exception_mail_send
from helper.rrr import RRReview
from threading import Thread
import time

# from requests.packages.urllib3.exceptions import InsecureRequestWarning

def default(init,order_details,client_data,portal_name,subjectline):
    if client_data['ipaddress']:
        checkip_flag,session=checkip(client_data['ipaddress'])
        page = session.get(order_details['order_accept_link'],verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
    else:
        session=requests.Session()
        page = session.get(order_details['order_accept_link'],verify=False)
        soup = BeautifulSoup(page.content, 'html.parser')
    if 'Unfortunately, this order is no longer available.' not in soup.text:
        ignored_msg,criteria_flag=init.criteria_check(order_details,portal_name)
        if criteria_flag:
            thread = threading.Thread(target=init.process_order, args=(session, order_details, client_data, soup,subjectline))
            thread.start()
        else:
            if 'EXCLUSIVE' in subjectline:
                subjectline = 'Exclusive'
                subject="Ignored Exclusive Order!!! - RRR-"+ignored_msg
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)            
            else:
                subjectline = 'Broadcasted'
                subject="Ignored Order!!! - RRR-"+ignored_msg
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)
    else:
        logging.info("Unfortunately, this order is no longer available.....")
        ignored_msg,criteria_flag=init.criteria_check(order_details,portal_name)
        if criteria_flag:
            if 'EXCLUSIVE' in subjectline:
                subjectline = 'Exclusive'
                subject="Ignored Exclusive Order!!! - RRR-"+"'Order Expired'"
                ignored_order(order_details['order_address'],order_details['order_type'],'Order Expired',order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)
                logging.info('Order Expired')
            else:
                subjectline = 'Broadcasted'  
                subject="Ignored Order!!! - RRR-"+"'Order Expired'"
                ignored_order(order_details['order_address'],order_details['order_type'],'Order Expired',order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)
        else:
            if 'EXCLUSIVE' in subjectline:
                subjectline = 'Exclusive'
                subject="Ignored Exclusive Order!!! - RRR-"+ignored_msg
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)                                        
            else:
                subjectline = 'Broadcasted'
                subject="Ignored Order!!! - RRR-"+ignored_msg
                ignored_order(order_details['order_address'],order_details['order_type'],ignored_msg,order_details['order_fee'],client_data,"RRReview",order_details['order_zip'],subject,order_details['order_received_time'],subjectline)
def main():
    try:
        portal_name=sys.argv[1]
        GMAIL_USERNAME=sys.argv[2]
        GMAIL_PASSWORD=sys.argv[3]
        # portal_name='RRR5'
        # GMAIL_USERNAME='rrrshawnacc@gmail.com'
        # GMAIL_PASSWORD='woxcsukpigavohux'
        # ctypes.windll.kernel32.SetConsoleTitleW(f"{portal_name}")
        count =0        
        while True:
            try:
                init=RRReview("")
                if count == 0:
                    count+=1
                    logger_mail(portal_name)
                cursorexec("order_updation","UPDATE",f"""UPDATE `servercheck` SET `event`='{datetime.now()}' where `portal`='{portal_name}' """)
                logging.info('checking New order')
                order_details,subjectline = init.fetch_details_mail(GMAIL_USERNAME,GMAIL_PASSWORD,portal_name)
                if order_details!="No Orders":
                    order_details=order_details[0]
                    order_received_time=datetime.now()                    
                    order_details.update({"order_received_time":order_received_time})
                    client_data=cursorexec("order_acceptance","SELECT",f"""SELECT * FROM `rrr` WHERE  `Email_address` = '{order_details['client_mail']}' LIMIT 1""")
                    init.client_data=client_data
                    if client_data != None:
                        if client_data["Status"]=="Active":
                            logging.info(f"ipaddress: {client_data['ipaddress']}")   
                            logging.info("%s acceptor for %s",portal_name,client_data['Client_name'])
                            # if client_data['Status'] == 'Active': #check if client is Active
                            logging.info('Client Active')
                            t1 = Thread(target=default, args=(init,order_details,client_data,portal_name,subjectline))
                            t1.start()                            
                        else:
                            inactive_inDB(client_data['Client_name'],portal_name)
                    else:
                        logging.info("Email Address not mapped")
                        exception_mail_send(portal_name,f"RRR-{portal_name}",f"Email Address not mapped----{order_details['client_mail']}")
                else:
                    logging.info("Waiting for new mail")
            except Exception as ex:
                exception_mail_send(portal_name,f"RRR-{portal_name}",f"Exception occured{str(ex)}")
                main()
    except Exception as ex:
        exception_mail_send(portal_name,f"RRR-{portal_name}",f"Exception occured: {str(ex)}")
        main()         
if __name__ == '__main__': main()