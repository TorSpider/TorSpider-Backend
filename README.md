# TorSpider-Backend
The database backend with which the spiders share their discoveries.

The database is a PostgreSQL database exposed via a Flask API.

The backend requires Python 3 and pip to begin with.


## Installation
The backend is responsible for managing the database and exposing the API.

### First Steps

Run the installation script to install and configure the required software.
The installer will run you through a set of questions to configure your instance.

```
$ sudo bash install.sh
=== TorSpider Backend Installer ===
This installed will walk you through the installation process.
<snip>
```

### SSL Certificates

#### Self-Signed Certificates
If you answered yes to installing self-signed certificates, your site is already set up.

**Warning:** We do not recommend running your site using self-signed certificates except for in testing or development.

#### Installing Your Own Certificates
In order to encrypt communication with the backend API, you'll need SSL certificates. You can obtain these from a number of sources, or generate your own. Once you've got them, you'll need to save them in the `/etc/nginx/certs/torspider/` folder. You should have the following two files:

`/etc/nginx/certs/torspider/backend.pem`
`/etc/nginx/certs/torspider/backend-key.pem`

Once those certificates are in place, you should be able to run the backend.

#### Using Let's Encrypt Certificates 
You can use a free certificate service from [Let's Encrypt](https://letsencrypt.org/).  

Install Let'sEncrypt
```
apt-get install -y software-properties-common python-software-properties
add-apt-repository -y ppa:certbot/certbot
apt-get update
apt-get install -y python-certbot-nginx
```

Update /etc/nginx/sites-available/backend.  You will need to replace any instance of `server_name _;` with `server_name mydomain.com;`
```
EXAMPLE!!!!
<snip>
server {
        # SSL configuration

        listen 443 ssl default_server;
        listen [::]:443 ssl default_server;

        server_name myspider_backend.com www.myspider_backend.com;
<snip>
```

Reload Nginx
```
systemctl reload nginx
```

Configure Let's Encrypt. 
Let's Encrypt will update your nginx file with the appropriate certificates
```
# For each domain enter -d <domain> 
certbot --nginx --deploy-hook /path/to/TorSpider-Backend/letsencrypt/deployhook.sh -d myspider_backend.com -d www.myspider_backend.com
```
Ensure you replace `/path/to` with the actual path of the TorSpider-Backend.

Enable automatic certificate renewal.  Let's Encrypt certs are only good for a few months.
```
systemctl enable certbot.timer
systemctl start certbot.timer
```

Reload Nginx
```
systemctl reload nginx
```

### Initialize the TorSpider Backend WebApp

Run the backend_manage.py script once to generate the instance/backend.cfg file:
```
$ python backend_manage.py
[+] Default configuration stored in instace/backend.cfg.
[+] Please edit instance/backend.cfg before running TorSpider backend.
```

Update your instance/backend.cfg file with the PostgreSQL DB settings that were provided to you during the automated installation.

If for some reason you want to run the site without SSL, ensure you set the USETLS setting to False.

### Populate the Database 

Next, you'll need to initialize the frontend database and seed it with values:
```
# Create the database tables
python3 backend_manage.py initdb
# Seed the initial required values
python3 backend_manage.py seed
```

If you receive psycopg2 errors during this phase, either PostgreSQL is not running or your username/password is incorrect.

### Generating Frontend API Keys

Before the frontend can connect and manage the backend, you'll need to generate a node ID and keys for the frontend. To do this, run:

```
python3 backend_manage.py create_frontend_node
```

The script will produce the necessary credentials for you. Be sure to write them down!


### Tune PostgreSQL for your server
PostgreSQL should be tuned based on the number of CPUs and memory available on your system.

Head over to [PgTune](http://pgtune.leopard.in.ua/) to create a custom tuned configuration based on your parameters.
Remember to restart postgres after you add them.

## Running the Backend
Let's get started:
`python3 backend_manage.py run`

Run it as a service:
`systemctl start torspider-backend`

You are now running your API, exposed on http://your_ip/api/onions

**Note**: You should receive `unauthorized` on a regular GET request, since you didn't pass your api keys. 

## Running Celery
Celery enables task scheduling in the background.

The installation script already installed the services, and they will start automatically on a reboot. 

Start the services manually:
```
systemctl start torspider-celery-beat
systemctl start torspider-celery-worker
```


## Upgrading The Database
If you are upgrading the application and you need to migrate any database changes, following these instructions:

```
python3 backend_manage.py db init
python3 backend_manage.py db migrate
python3 backend_manage.py db upgrade
```

This will initialize the database migration scripts and migrate to the new format of the tables in models.py