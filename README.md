# DS_project

This is a group project that explores aspects of the Starcraft II ladder, mmr, and win ratio using Python scripts.

# How to use

## Setting up virtual env

1. Clone the repository to your local machine
2. Set up the virtual env and install the dependencies:
```
$python3 -m venv env
$source env/bin/activate
(env)$pip install -r requirements.txt
```

## Setting up the configurations
1. Go to the Blizzard Battle.net API and register an account.
2. Get your own client ID and secret. Save them into a ```.env``` file under /API requests/ in the following format:
```
CLIENTID=<your client id>
SECRET=<your client secret>
```
3. Set up your own mySQL server. This can be done on a local machine or using a web service provider like the RDS service on AWS. Once the database server is set up, input its credentials into a ```.env``` file in the following format:
```
DBHOSTNAME=<path to the database>
DBNAME=<your database name>
DBUSERNAME=<your database username>
PASSWORD=<your database password>
```

## Running the code
1. Once everything is set up, simply execute ```task.py``` under the /API requests/ folder:
```
python3 task.py
```
2. Alternatively, use crontab job scheduling for periodic updates of player and matches data:
```
0 0 0 * * python3 task.py
```
>It is recommended that you use a cloud instance like AWS EC2 for crontab. For details of how cron job scheduling works check their documentations check [the Wikipedia page.](https://en.wikipedia.org/wiki/Cron)