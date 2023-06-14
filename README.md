Generates BYOND Accounts automatically. 

Before running install the dependencies and update the ENV file

Install Dependencies
```python
pip install -r requirements.txt
```

Example ENV File
```
AUTOMATIC=True
WEBHOOK=https://discord.com/api/webhooks/xxxxxxxxxxxxxxxxxx/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FAILURE_TIMER=120
```

Setting Automatic to false will ask the user for the name of the account before generating. 
Failure Timer indicates how long the script will wait to check ratelimited status

Works on most systems, however does not work on headless linux installs.
