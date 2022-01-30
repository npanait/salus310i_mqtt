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
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import shutil
import json 
import paho.mqtt.client as mqtt
import random


__author__ = "Nicolae Panait"
__version__ = "0.2.0"
__license__ = "MIT"

# MQTT constants
MQTT_HOST="192.168.64.128"
MQTT_PORT=1883
MQTT_KEEPALIVE_INTERVAL = 45
MQTT_TOPIC = "GenusOne"
MQTT_MESSAGE = {"SensorTime":datetime.now().isoformat(),
                        "CurrentTemperature":{"Value":0, "Type":"temp", "Unit":"C"},
                        "TargetTemperature":{"Value":0,  "Type":"temp", "Unit":"C"}, 
                        "Program":{"Value":"HEATING AUTO"},
                        "Gas":{"Value":0,  "Type":"boolean"}
                }


#MQTT_MSG=json.dumps({"sepalLength": "6.4","sepalWidth":  "3.2","petalLength": "4.5","petalWidth":  "1.5"});
# Define on_publish event function
def on_publish(client, userdata, mid):
    logging.info("MQTT publish OK:, mid {}".format(mid))
    #print ("Message Published...")

def on_connect(client, userdata, flags, rc):
    if rc==0:
        client.connected_flag=True #set flag
        #client.subscribe(MQTT_TOPIC)
        #client.publish(MQTT_TOPIC, MQTT_MSG)
        print("Client {} connected OK".format(client.client_id))
    else:
        logging.error("MQTT Bad connection Returned code=",rc)
    

def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload) # <- do you mean this payload = {...} ?
    payload = json.loads(msg.payload) # you can use json.loads to convert string to json
    #print(payload['sepalWidth']) # then you can check the value
    client.disconnect() # Got message then disconnect

# Initiate MQTT Client
client_id = f'python-mqtt-{random.randint(0, 1000)}'
mqttc = mqtt.Client(client_id)

# Register publish callback function
mqttc.on_publish = on_publish
mqttc.on_connect = on_connect
mqttc.on_message = on_message

# Connect with MQTT Broker
mqttc.username_pw_set(secrets.mqtt_user, secrets.mqtt_pass)


# Loop forever
#mqttc.loop_forever()

#This URL will be the URL that your login form points to with the "action" tag.
POST_LOGIN_URL = 'https://salus-it500.com/public/login.php?lang=en'

#This URL is the page you actually want to pull down with requests.
REQUEST_URL = 'https://salus-it500.com/public/control.php?devId=67111755'  #67111755 is my device id - replace this with yours
payload = {
    'IDemail': secrets.salus_user,
    'password': secrets.salus_pass,
    'login': "Login"
}

def nested_set(dic, keys, value):
    for key in keys[:-1]:
        dic = dic.setdefault(key, {})
    dic[keys[-1]] = value

def main():
    """ Main entry point of the app """
    shutil.copyfile('app.log', 'app-{}.log'.format(datetime.now()))
    logging.basicConfig(filename='app.log', filemode='w',format='%(asctime)s - %(message)s', level=logging.INFO)
    with requests.Session() as session:
        retry = Retry(total=7,connect=5, backoff_factor=3)
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)

        while True:
            #print(50*'-')
            #print(datetime.now())

            try:
                            
            #error treatment
                post = session.post(POST_LOGIN_URL, data=payload)
                r = session.get(REQUEST_URL)
                if r:
                    # Connect to MQTT broker
                    mqttc.connect(MQTT_HOST, MQTT_PORT, MQTT_KEEPALIVE_INTERVAL)
                    MQTT_MESSAGE["SensorTime"] = datetime.now().isoformat()
                    #request data parsed by beautiful soup
                    soup = bs.BeautifulSoup(r.text,'html.parser')
                    # Finds the Current temperature and saves it to the dictionaty
                    # nested_set(d, ['person', 'address', 'city'], 'New York')
                    nested_set(MQTT_MESSAGE, ["CurrentTemperature","Value"], float( soup.find(id='current_room_tempZ1').get_text() ) )
                    nested_set(MQTT_MESSAGE, ["TargetTemperature","Value"], float( soup.find(id='current_tempZ1').get_text() ) )
                    logging.info('Current temperature is: {:03.1f} with target {:03.1f}'.format(MQTT_MESSAGE["CurrentTemperature"]["Value"],MQTT_MESSAGE["TargetTemperature"]["Value"]) )  #<p id="current_room_tempZ1">23<span class="lastDigit">.9</span></p>
                    # Finds the Heating note indicator and saves it to dictionary
                    nested_set(MQTT_MESSAGE, ["Program","Value"],soup.find('p', class_='heatingNote').get_text().strip() )
                    logging.info(MQTT_MESSAGE["Program"]["Value"])  #<p class="heatingNote heatingAuto">HEATING AUTO</p>
                    # <img id="CH1onOff" class="CH1onOff" src="assets/flame.png" alt="Zone 1 is on">
                    

                    flame = soup.find("img", class_="CH1onOff display",id="CH1onOff") #soup.find('img', id_ ='CH1onOff')  class="CH1onOff display"
                    #print(flame)
                    if (flame is None):
                        nested_set(MQTT_MESSAGE, ["Gas","Value"],0)
                        logging.info('Gaz-Pornit' if flame else 'Gaz-Oprit')
                    else:
                        nested_set(MQTT_MESSAGE, ["Gas","Value"],1)
                        logging.info('Gaz-Pornit' if flame else 'Gaz-Oprit')
                    #print("publishing mqtt")
                    mqttc.publish(MQTT_TOPIC, payload=json.dumps(MQTT_MESSAGE), qos=0, retain=False)
                else:
                    logging.error('Salus server not available')
            except requests.exceptions.Timeout:
                # Maybe set up for a retry, or continue in a retry loop
                logging.warning(requests.exceptions.Timeout)
                time.sleep(300)
            #except requests.exceptions.TooManyRedirects:
                # Tell the user their URL was bad and try a different one
            except requests.exceptions.ConnectionError:
                logging.warning(requests.exceptions.ConnectionError)
                time.sleep(300)
            except requests.exceptions.RequestException as e:
                # catastrophic error. bail.
                logging.critical(e)
                raise SystemExit(e)
            # If all went good, disconnect from MQTT brocker
            mqttc.disconnect()
            time.sleep(300)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()


