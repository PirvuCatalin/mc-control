from flask import Flask, render_template, request
import requests
from urllib3.exceptions import InsecureRequestWarning
from flask_apscheduler import APScheduler
import time
import datetime
from minecraft_query import *

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# change these
access_pass = '<generate-this-randomly-and-share-with-ui-users>'
vm_id = 1234
PVEAPIToken = '<proxmox-api-token-for-specific-vm>'
proxmox_url = '<better-use-localhost-if-possible>'
port = 8321
time_before_stopping_server = 60 * 10 # 10 minutes

status_url = f'{proxmox_url}/api2/json/nodes/proxmox/qemu/{vm_id}/status/current'
start_url = f'{proxmox_url}/api2/json/nodes/proxmox/qemu/{vm_id}/status/start'
stop_url = f'{proxmox_url}/api2/json/nodes/proxmox/qemu/{vm_id}/status/stop'
headers = {'Authorization': f'PVEAPIToken={PVEAPIToken}'}

players_online = 0
time_last_activity = None

app = Flask(__name__)
scheduler = APScheduler()
scheduler.init_app(app)

@app.route('/start')
def start():
    password = request.args.get('parola')
    if password != access_pass:
        return 'Parola incorecta!', 400
    requests.post(url=start_url, headers=headers, verify=False)
    return 'Serverul va porni imediat!', 200

@app.route('/stop')
def stop():
    password = request.args.get('parola')
    if password != access_pass:
        return 'Parola incorecta!', 400
    requests.post(url=stop_url, headers=headers, verify=False)
    return 'Serverul a fost oprit!', 200

@app.route('/status')
def status():
    password = request.args.get('parola')
    if password != access_pass:
        return 'Parola incorecta!', 400
    r = requests.get(url=status_url, headers=headers, verify=False)
    res = r.json()
    status = res['data']['status']
    if status == 'stopped':
        return 'Serverul este oprit.', 200
    elif status == 'running':
        return f'Serverul este pornit. Sunt {players_online} playeri online (posibil incorect).', 200
    else:
        return 'Nu stiu starea serverului ;(.', 200

@app.route('/')
def home():
    return render_template('index.html')

@scheduler.task('cron', id='get_note', minute='*/5') # every 5 minutes
def check_server():
    r = requests.get(url=status_url, headers=headers, verify=False)
    res = r.json()
    status = res['data']['status']
    if status == 'running':
        query = MinecraftQuery("192.168.1.248", 25565)
        global players_online
        global time_last_activity
        query_result = query.getResult()
        players_online = query_result['OnlinePlayers']
        print(f'[{datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S")}] Sunt {players_online} playeri online.')
        if players_online == 0:
            if time_last_activity is None:
                time_last_activity = time.time()
            elif time.time() - time_last_activity > time_before_stopping_server:
                print(f'[{datetime.datetime.now().strftime("%d/%b/%Y %H:%M:%S")}] Vom opri serverul. Nu a fost niciun player on in ultimele 10 minute.')
                requests.post(url=stop_url, headers=headers, verify=False)
        else:
            time_last_activity = time.time()
    else:
        time_last_activity = None

if __name__ == '__main__':
    scheduler.start()
    app.run(debug=False, host='0.0.0.0', port=port)