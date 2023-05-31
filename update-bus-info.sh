#! /bin/bash

set -o allexport && source .env && set +o allexport
cd busAlertsBackend
git checkout main
python3 refreshBusData.py
git add .
git commit -m "refresh bus data"
git push 'https://'$GITUSER':'$TOKEN'@github.com/'$GITUSER'/busAlerts2.git' main
git checkout prod
git merge main --commit -m "update bus info in prod"
git push 'https://'$GITUSER':'$TOKEN'@github.com/'$GITUSER'/busAlerts2.git' prod
cd ..
sudo docker-compose down
sudo docker-compose build
sudo docker-compose up -d