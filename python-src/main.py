#!/usr/bin/env python3
"""
Module salus310i_mqtt
"""
import secrets
import requests
import bs4 as bs
from datetime import datetime
import time
import logging

__author__ = "Nicolae Panait"
__version__ = "0.1.0"
__license__ = "MIT"

#This URL will be the URL that your login form points to with the "action" tag.
POST_LOGIN_URL = 'https://salus-it500.com/public/login.php?lang=en'

#This URL is the page you actually want to pull down with requests.
REQUEST_URL = 'https://salus-it500.com/public/control.php?devId=67111755'  #67111755 is my device id - replace this with yours
payload = {
    'IDemail': secrets.salus_user,
    'password': secrets.salus_pass,
    'login': "Login"
}

def main():
    """ Main entry point of the app """
    logging.basicConfig(filename='app.log', filemode='w',format='%(asctime)s - %(message)s', level=logging.INFO)
    with requests.Session() as session:
        while True:
            #print(50*'-')
            #print(datetime.now())
            post = session.post(POST_LOGIN_URL, data=payload)
            r = session.get(REQUEST_URL)
            if r:
                
                #request data parsed by beautiful soup
                soup = bs.BeautifulSoup(r.text,'html.parser')
                # Finds the Current temperature
                logging.info('Current temperature is: {:03.1f}'.format(float(soup.find(id='current_room_tempZ1').get_text())))  #<p id="current_room_tempZ1">23<span class="lastDigit">.9</span></p>
                # Finds the Heating note indicator
                logging.info(soup.find('p', class_='heatingNote').get_text().strip())  #<p class="heatingNote heatingAuto">HEATING AUTO</p>
                # <img id="CH1onOff" class="CH1onOff" src="assets/flame.png" alt="Zone 1 is on">
                flame = soup.find('img',id_ ='CH1onOff')
                logging.info('Gaz-Pornit' if flame else 'Gaz-Oprit')
            else:
                logging.error('Salus server not available')
            time.sleep(60)
        

if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()


