# DS_project

This is a group project that explores aspects of the Starcraft II ladder, mmr, and win ratio using Python scripts.

# How to use

1. Clone the repository to your local machine
2. Go to the Blizzard Battle.net API and register an account.
3. Get your own client ID and secret. Save them into a ```.env``` file under /API requests/ in the following format:

```
CLIENTID=<your client id>
SECRET=<your client secret>
```
4. Set up your own mySQL server. This can be done on a local machine or using a web service provider like AWS. Once the database server is set up, input its credentials into a ```.env``` file under ```dataframes/``` in the following format:

```
HOSTNAME=<path to the database>
DBNAME=<your database name>
DBUSERNAME=<your database username>
PASSWORD=<your database password>
```

5. Create a virtual environment in Python and activate it:

```
python3 -m venv env
source env/bin/activate
```

7. Install the required packages:

```
pip install -r requirements.txt
```

7. Run ```APIrequests.py``` under the /API requests/ folder.

```
python3 APIrequests.py
```
