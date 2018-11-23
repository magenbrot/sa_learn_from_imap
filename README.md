# sa_learn_from_imap.py

Train spamassassin from an IMAP mailbox

## CLONE THE REPO

```bash
cd /opt
git clone https://github.com/magenbrot/sa_learn_from_imap.git
```

## PREREQUISITES

Debian OS:

Setup virtualenv and install required modules.

```bash
sudo apt install build-essential curl python3-venv

cd sa_learn_from_imap
python3 -m venv env/python3
source env/python3/bin/activate
pip install -r requirements.txt
```

## USAGE

The script has 3 required, positional arguments. The IMAP-host, -user and the -password. By default it assumes that 
your SPAM mails are sorted in a folder called 'spam' and your HAM mails are filed in 'ham'.

This can be changed with the parameters ```--spam-folder``` and ```--ham-folder```. It needs a working directory, this 
is ```/tmp/sa-learn``` by default and can be changed with the ```--directory``` parameter. Finally you can specify the 
sa-learn script it should use with ```--sa-learn```. This defaults to ```/usr/bin/sa-learn```.

Please call the script with the user you're running SpamAssassin with. In my case it's ```root``` (I'm using the 
Proxmox Mail Gateway).

Example (run with python3, either directly or in the venv from above):
```bash
./sa_learn_from_imap.py mail.mymails.org 'filter@mymails.org' 'password123$'
```

A cronjob could look like this, put this in ```/etc/cron.d/sa-learn-ham-spam```:
```bash
#MAILTO="postmaster@mymails.org"
MAILTO=""

# run with bash, as sh doesn't support 'source'
SHELL=/bin/bash

15 * * * * root source /opt/sa_learn_from_imap/env/python3/bin/activate && \\
           /opt/sa_learn_from_imap/sa_learn_from_imap.py mail.mymails.org 'filter@mymails.org' 'password123$'
```

## TODO

more error handling...

![cat typing](https://i.imgur.com/U47uVtE.gif)