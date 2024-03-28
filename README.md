# To deploy use these cmd:

## First, login using:
- heroku login

## Initialize a git repository in a new or existing directory
- git init
- heroku git:remote -a mqtt-listener-air-monitoringv2

## Deploy your applicationCommit your code to the repository and deploy it to Heroku using Git.
- git add .
- git commit -am "make it better"
- git push heroku master

## TO RUN:
- heroku ps:scale worker=1

## TO STOP:
- heroku ps:scale worker=0
