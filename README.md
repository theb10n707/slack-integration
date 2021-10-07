## Introduction
This slack integration is used to listen for syslog messages from Cisco Networking Devices and it posts them in a Slack Channel. 
The post will also have buttons (actions) for tasks such as creating a JIRA ticket, SSHing to the device, and chart generation 
on the number of syslogs over a time period. These are just a few features, but you can easily add many more tasks.

This system is built off of Flask with MongoDB, Redis, and Celery (To perform the Actions from Slack). This app
will run with Gunicorn and sit behind NGINX

Ports
```
REDIS=6379  
MONGODB=27017  
Syslog Server=5040  
Gunicorn=5050  
NGINX=8080 
```
 

## Requirements
1. Please have docker installed on your laptop
2. You will need to add JIRA and SLACK credentials to the .env file in the base folder
3. Make sure your Slack Token has permissions to upload files, make them public, read/write 
permissions in slack channel
4. Be in a great mood!!! 

#### slack_integration/.env
```buildoutcfg
# Slack Credentials
SLACK_VERIFICATION_TOKEN=<ENTER DATA>
SLACK_USER_OAUTH_TOKEN=<ENTER DATA>
SLACK_CHANNEL=<ENTER DATA>

# JIRA Credentials
JIRA_URL=<ENTER DATA>
JIRA_API_TOKEN=<ENTER DATA>
JIRA_EMAIL=<ENTER DATA>
JIRA_PROJECT=<ENTER DATA>

# Nginx
NGINX_PORT=8080

# MongoDB
DB_ROOT_USER=root
DB_ROOT_PW=root
DB_NAME=root
DB_USER=root
DB_PASSWORD=root
MONGODB_PORT=27017
MONGODB_HOST=mongodb://root:root@mongo:27017/slack_integration?authSource=admin

# Redis
REDIS_PORT=6379

# Syslog Server
HOST=0.0.0.0
PORT=5050

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Flask Config
FLASK_PORT=5040
FLASK_IP_ADDRESS=0.0.0.0

```

## Getting Started
1. Build `docker-compose --env-file .env build`
2. Start `docker-compose --env-file .env up -d`
3. Check if containers are up `docker-compose ps`
4. Go to `locahost:8080` on the browser and verify you get a response that says "API is Up"
5. If you wish to change the port, it will be the NGINX port in .env

## To test the app
1. You can use nc on Mac to send syslogs. here is the sample command. NOTE that the syslog port is 5050:
```
echo  "<190>1531142: Sep 21 17:27:41.305: %MODULE-2-MOD_DIAG_FAIL: Module 2 (Serial number: JAE230418J0) reported failure Ethernet2/1due to Fatal runtime Arb error. (DevErr is bitmap of failed modules) in device DEV_XBAR_COMPLEX (device error 0x2)" | nc -p 7 -u localhost 5050
```
2. Check your Slack app for the message :D

## To Be Added
1. Retry mechanism for all API calls
2. Tests
3. API Response error handling for Users. For example: If the API fails to query data, respond to the request with an error message