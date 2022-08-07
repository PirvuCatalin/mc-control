# Minecraft Control (mc-control)

Note: the name might be misleading, but it can actually start/stop/get-status of any VM in Proxmox. Minecraft was my use case.

Branch `mc-autostop` also contains a checker for auto stopping the VM if there are no players for atleast 10 minutes.

<br>

### Simple Flask app running in Docker used for controlling a single VM that runs on Promox.

<br>

Available controls:
 - start VM
 - stop VM
 - get VM status

## Prerequisites + Configuration

0. I assume Proxmox is already setup and you have a VM ready to be controlled
1. Generate an API Token for the VM that you want to control and set it as the variable `PVEAPIToken` in mc-control.py
2. Generate a random string for the password ("Acces" to be used on the UI) - set it as the variable `access_pass` in mc-control.py. Example of a generator [here](https://www.random.org/strings/?num=1&len=20&digits=on&upperalpha=on&loweralpha=on&unique=on&format=html&rnd=new)
3. Set the `vm_id` in mc-control.py
4. Set the `proxmox_url` in mc-control.py

Note: Containers (LXC/CT) can also be controlled, but you need to change the URLs (lines 14-17 in mc-control.py). More info [here][1].

## How to use

1. Clone this repo and cd mc-control
2. Configure the variables in `mc-control.py` as explained above
3. `docker image build . -t mc-control`
4. `docker run -p 8321:8321 -d mc-control`
5. Open a browser at http://localhost:8321

If you prefer (like I do) to use docker-compose, you can skip step 4 and just run `docker compose up -d`. This will also ensure that the container starts on boot.

[1]: <https://pve.proxmox.com/pve-docs/api-viewer/index.html#/nodes/{node}/lxc/{vmid}/status/start>

## What it actually does

Basically, the app was created for allowing a simple user to start/stop a VM on demand. 

The backend is serving an index.html file where the user can start, stop or see the status of a specific VM. It's also taking care of the calls to Proxmox. The Proxmox API Token is specifically allowed to control only the VM that this script targets, otherwise if someone steals it, RIP any VMs. The Acces Pass is a randomly generated password that is shared with people who can manage this VM. It's hardcoded in mc-control.py, so I'm basically the only one that knows it (for now).

The UI can be seen below. 
It's pretty straightforward. 

![the ui](/img/ui.png)

It will require an "Acces" token (hardcoded in mc-control.py as `access_pass`), then you can trigger the Start / Stop of the VM (configured through the `vm_id` and `proxmox_url` in mc-control.py). 

The status of the VM ("oprit" = stopped, "pornit" = running) will refresh every 5 seconds as long as you keep the page open (configurable in index.html). The Acces token will also be added to the browser's cookies (with technically no expiration date) as `mc-control-acces`.