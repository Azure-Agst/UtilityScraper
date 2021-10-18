# Scheduling Utility Scraper

## Linux

First, clone the repo to somewhere common, like `/opt`, and make sure all dependencies are met. (i.e. Firefox/python3 installed, geckodriver in path.)

Configure `config.ini` to your liking

Make a new service user using `useradd` called something like `utilpy`.

Now, make a file at `/etc/systemd/system/` called `UtilityScraper.service` which contains the following:

```ini
[Unit]
Description=Scrapes utility web portal for data
After=network.target
Wants=UtilityScraper.timer

[Service]
Type=oneshot
User=utilpy
ExecStart=/usr/bin/env python3 /your/path/here/utilityscraper.py
WorkingDirectory=/your/path/here

[Install]
WantedBy=multi-user.target
```

Also make `UtilityScraper.timer` in the same location and make it contain the following:

```ini
[Unit]
Description=Scrapes utility web portal for data
Requires=UtilityScraper.service

[Timer]
Unit=UtilityScraper.service
OnCalendar=Sun *-*-* 00:00:01

[Install]
WantedBy=timers.target
```

Now open bash and enter the following:

```bash
$ sudo sudo systemctl start WeatherReport # loads timer/service
$ sudo sudo systemctl enable WeatherReport # tells timer to continue after reboot
```

## Mac

First, clone the repo to somewhere common, like `/Users/Shared`, and make sure all dependencies are met. (i.e. Firefox/python3 installed, geckodriver in path.)

At the moment, I'm unsure of how to make service users on Mac, so I usually run them on an isolated machine using a general admin account I made explicitly for running services. If you wish to research how to make service users of your own, good luck. :)

You'll also need to come up with an ID for this service. Usually it's a somein you own, backwards, and with the project name appended to the end, i.e `dev.azureagst.utilscraper`. If you don't own a website, it's fine, just use the format `local.your_username.utilscraper`.

Create a plist file using that ID as the name in `/Library/LaunchDaemons` and make it have the following:

```plist
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
        <dict>
                <key>Label</key>
                <string>your.id.here</string>
                <key>ProgramArguments</key>
                <array>
                        <string>/usr/bin/env</string>
                        <string>python3</string>
                        <string>/your/path/here/utilityscraper.py</string>
                </array>
                <key>WorkingDirectory</key>
                <string>/your/path/here</string>
                <key>RunAtLoad</key>
                <true/>
                <key>StartCalendarInterval</key>
                <dict>
                    <key>Weekday</key>
                    <integer>0</integer>
                </dict>
                <key>UserName</key>
                <string>yourserviceuser</string>
                <key>GroupName</key>
                <string>admin</string>
        </dict>
</plist>
```

Now run these commands:

```zsh
% sudo launchctl load /Library/LaunchDaemons/your.id.here.plist # load module
% sudo launchctl enable your.id.here # register to run after reboot
```