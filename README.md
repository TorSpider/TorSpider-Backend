# TorSpider-Backend
The database backend with which the spiders share their discoveries.

The database is a PostgreSQL database exposed via a Flask API.

The backend requires Python 3 and pip to begin with.


## Installation
The backend is responsible for managing the database and exposing the API.

Update your backend.cfg file with the PostgreSQL DB settings and ensure the database and user are created.

Ensure you have installed the requirements:
`pip3 install -r requirements.txt`

Run the following command to initialize the database and create the tables:
`python3 backend_manage.py initdb`

Run the following command to seed the database:
`python3 backend_manage.py seed`

If you'd like to install the backend as a service:
Please note, we assume torspider is installed as the torpsider user in /home/torspider.
1. Run `sudo cp init/torspider-backend.service /etc/systemd/system/`
2. Run `sudo systemctl daemon-reload`
3. Run `sudo systemctl enable torspider-backend`

## Running the Backend
Let's get started:
`ptyhon3 backend_manage.py run`

Run it as a service:
`systemctl start torspider-backend`

You are now running your API, exposed on http://your_ip:1080

## Set up Nginx
Nginx is used to expose both the frontend (1081) and backend (1080) websites on one port (80) to regular users.
Ensure your have Nginx installed: `apt-get install nginx`

Copy the provided nginx config file to /etc/nginx/sites-available:
`cp nginx_conf/default /etc/nginx/sites-available`

Restart Nginx:
`service nginx restart`
