# TorSpider-Backend
The database backend with which the spiders share their discoveries.

The database is a PostgreSQL database exposed via a Flask API.

The backend requires Python 3 and pip to begin with.


## Installation
The backend is responsible for managing the database and exposing the API.

### First Steps

First, ensure you have installed the requirements:
`pip3 install -r requirements.txt`

Next, run the backend_manage.py script once to generate the backend.cfg file:
```
$ python backend_manage.py
[+] Default configuration stored in backend.cfg.
[+] Please edit backend.cfg before running TorSpider backend.
```

Update your backend.cfg file with the PostgreSQL DB settings and ensure the database and user are created.

Next, you'll need to initialize the frontend database and seed it with values:
```
python3 backend_manage.py initdb
python3 backend_manage.py seed
```

### SSL Certificates

In order to encrypt communication with the backend API, you'll need SSL certificates. You can obtain these from a number of sources, or generate your own. Once you've got them, you'll need to save them in the `/etc/nginx/certs/torspider/` folder. You should have the following two files:

`/etc/nginx/certs/torspider/cert.crt`
`/etc/nginx/certs/torspider/cert.key`

Once those certificates are in place, you should be able to run the backend.

**Note:** These certificates are the same certificates as the ones used in the frontend installation.

### Installing the Backend as a Service

If you'd like to install the backend as a service:
Please note, we assume torspider is installed as the torpsider user in /home/torspider.
1. Run `sudo cp init/torspider-backend.service /etc/systemd/system/`
2. Run `sudo systemctl daemon-reload`
3. Run `sudo systemctl enable torspider-backend`

### Generating Frontend API Keys

Before the frontend can connect and manage the backend, you'll need to generate a node ID and keys for the frontend. To do this, run:

```
python3 backend_manage.py create_frontend_node
```

The script will produce the necessary credentials for you. Be sure to write them down!

## Running the Backend
Let's get started:
`ptyhon3 backend_manage.py run`

Run it as a service:
`systemctl start torspider-backend`

You are now running your API, exposed on http://your_ip:1080

## Set up Nginx
Nginx is used to expose both the frontend (1081) and backend (1080) websites on one port (80) to regular users.
Ensure your have Nginx installed: `apt-get install nginx`

Copy one of the provided nginx config files to /etc/nginx/sites-available.

If you are installing the backend on a separate system from the frontend, copy the backend configuration as follows:

`cp nginx_conf/backend /etc/nginx/sites-available/default`

However, if you are running both the backend and frontend on the same system, copy the combined configuration as follows:

`cp nginx_conf/combined /etc/nginx/sites-available/default`

After copying the appropriate configuration file, restart Nginx:
`service nginx restart`

Once this is complete, you should be able to access the backend from http://your_ip/api/.
