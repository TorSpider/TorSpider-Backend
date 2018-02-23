# TorSpider-Backend
The database backend with which the spiders share their discoveries.

The database is a PostgreSQL database exposed via a Flask API.  


## Usage
The backend is responsible for the database and exposing the API.

Update your app/config.py file with the PostgreSQL DB settings and ensure the database is created.

Ensure you have installed the requirements:
`pip3 install -r requirements.txt` 

Run the following command to initialize the database and create the tables:
`python3 backend_manage.py initdb`

Run the following command to seed the database:
`python3 backend_manage.py seed`

Let's get started:
`ptyhon3 backend_manage.py run`

You are now running your API, exposed on http://your_ip:1080

## Set up Nginx
Nginx is used to expose both the frontend (1081) and backend (1080) websites on one port (80) to regular users. 
Ensure your have Nginx installed: `apt-get install nginx`

Copy the provided nginx config file to /etc/nginx/sites-available:
`cp nginx_conf/default /etc/nginx/sites-available`

Restart Nginx:
`service nginx restart`
