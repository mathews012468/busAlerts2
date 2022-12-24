To run this project, just do:

```
docker-compose build
docker-compose up
```

## TODO
1. Make website default to https (done)
2. SEO
3. Auto recharge twilio (done)
4. Backup certificates and prod changes to default.conf and docker-compose.yaml (done, created new branch called prod to save prod changes, backed up certificates on separate private github repo)
5. Logging
6. Auto start server when computer turns on/restarts
7. Autocompletion suggestions for bus route
8. https strict transport security (done)
9. Disable old versions of TLS
10. Download image locally (done)
11. Server-side input validation
12. Reject calls (done, delete webhook)
13. Reject text messages (done, delete webhook)
14. Add script to refresh bus info
15. Make sure IP doesn't change (static IP maybe?) (done, and yes it was static ip)