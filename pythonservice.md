First navigate to:

/etc/systemd/system
Then create a new service as root:

sudo nano example.service
Make your service file like this:

[Unit]
Description=Restarts example.py if it closes

[Service]
User=your username
WorkingDirectory=/directory/of/script
ExecStart=/usr/bin/python3 /directory/of/script/example.py
Restart=always

[Install]
WantedBy=multi-user.target
Then type this in to have systemd reload the service files.

sudo systemctl daemon-reload
Then you can start your service:

sudo systemctl start example.service
Finally, check the status of your service:

sudo systemctl status example.service