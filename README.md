# Lola Daily Announcement

Perpetuation of Lola's daily announcement for the holy object.

![Screenshot of a notification](./screenshot-notification.png)

## Usage

Make sure `notify-send` is installed (eg on Debian based systems `apt
install libnotify-bin`), then simply call the
[lola_daily_announcement.py](lola_daily_announcement.py) script.

The default is to send a desktop notification but one can use standard
output with the `--stdout` parameter:

``` bash
$ ./lola_daily_announcement.py --stdout
Chalut ! Aujourd'hui, Mitanche 2, c'est la Saint-symptôme.
Bonne fête à tous les symptômes 🎆
```

### As a user service

To enable the provided systemd timer:

``` bash
$ mkdir -p ~/.local/bin ~/.config/share/systemd/user
$ cp lola-daily-announcement.{service,timer} ~/.local/share/systemd/user/
$ cp lola_daily_announcement.py ~/.local/bin/
$ systemctl start --user lola-daily-announcement.timer
``` 

To deploy for all users, move the service file to
`/usr/share/systemd/user/` and the script to `/usr/local/bin`.

## Credits

See https://github.com/tobozo/SaintObjetBot for credits and sources.
