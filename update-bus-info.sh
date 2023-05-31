#! /bin/bash

set -o allexport && source .env && set +o allexport
cd busAlertsBackend
git checkout main
source venv/bin/activate
pip install -r requirements.txt
python refreshBusData.py
git add .
git commit -m "refresh bus data"
git push 'https://'$GITUSER':'$TOKEN'@github.com/'$GITUSER'/busAlerts2.git' main
git checkout prod
git merge main --commit -m "update bus info in prod"
git push 'https://'$GITUSER':'$TOKEN'@github.com/'$GITUSER'/busAlerts2.git' prod