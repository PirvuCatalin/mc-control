from flask import Flask, render_template, request
import requests
from urllib3.exceptions import InsecureRequestWarning

# Suppress only the single warning from urllib3 needed.
requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

# change these
access_pass = '<generate-this-randomly-and-share-with-ui-users>'
vm_id = 1234
PVEAPIToken = '<proxmox-api-token-for-specific-vm>'
proxmox_url = '<better-use-localhost-if-possible>'
port = 8321

status_url = f'{proxmox_url}/api2/json/nodes/proxmox/qemu/{vm_id}/status/current'
start_url = f'{proxmox_url}/api2/json/nodes/proxmox/qemu/{vm_id}/status/start'
stop_url = f'{proxmox_url}/api2/json/nodes/proxmox/qemu/{vm_id}/status/stop'
headers = {'Authorization': f'PVEAPIToken={PVEAPIToken}'}

app = Flask(__name__)

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
        return 'Serverul este pornit.', 200
    else:
        return 'Nu stiu starea serverului ;(.', 200

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=port)