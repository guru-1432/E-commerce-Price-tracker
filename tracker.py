from bs4 import BeautifulSoup
import json
import requests
from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# Read config file to get the url to scrape , the class id and  schedular interval
with open('config.json', 'r') as config_file:
    config_json = json.load(config_file)

 
url = config_json['url']
web_hook = config_json['web_hook']
scheduler_interval = config_json['Scheduler_interval'] 

# Method to send slack notification
def notification(message):
    msg_post = json.dumps({'text': message})
    response = requests.post(web_hook,data = msg_post)

def scraper():
    print('in scraper')
    page = requests.get(url)
    soupe =  BeautifulSoup(page.content,'lxml')
    price = soupe.find("div", {"class": '_30jeq3 _16Jk6d'}).get_text()
    price = int(price.replace(',','')[1:])

    if price < config_json["desired_price"]:
        notification(f'Price droped : \n {url}')  

# ASP scheduler setup
scheduler = BackgroundScheduler()
scheduler.configure()
scheduler.add_job(scraper, 'interval', seconds=scheduler_interval)


# cofig the routes for to start and stop the tracking

# Route to start the Tracker 
@app.route('/start',methods=['GET'])
def start():
    if scheduler.running :
        return 'Already Tracking'
    else:
        scheduler.start()
        return 'Tracking Started'

# Route to pause the tracker        
@app.route('/pause',methods=['GET'])
def pause():
    if scheduler.running:
        scheduler.pause()
        return 'Tracking Paused'
    else :
        return 'No job runnning'

#Route to stop the tracker
@app.route('/stop',methods=['GET'])
def stop():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        return 'shuting down'
    else:
        return 'Scheduler not running'

#Route to check the current status of the tracker 
@app.route('/status',methods = ['GET'])
def status():
    status  = {0 : 'STOPPED' , 1: 'RUNNING',2: 'PAUSED'}
    return str(status[scheduler.state])
    
# Start Flask app
if __name__  == "__main__":
    app.run(debug=True)



