#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Train spamassassins bayes filter with mails fetched from an IMAP account


"""

from __future__ import print_function
from shutil import rmtree
import os
import sys

try:
    import imaplib
    import argparse
    import tempfile

except ImportError as error:
    print("Missing python module: {}".format(error))
    sys.exit(255)

__author__ = "Oliver Völker"
__contact__ = "info@ovtec.it"
__copyright__ = "Copyright 2018, OVTEC Völker IT"
__license__ = "GPLv3"
__maintainer__ = "Oliver Völker"
__status__ = "Production"
__version__ = "0.1"


def process_mailbox(mail, folder, directory):
    """ Fetch (and delete) mails from IMAP mailbox and dump them to a folder """

    typ, msgs = mail.search(None, 'ALL')
    if typ != 'OK':
        print("No messages found!")
        return

    for emailid in msgs[0].split():
        resp, data = mail.fetch(emailid, "(RFC822)")
        if resp != 'OK':
            print("Failed to fetch message", emailid)
            return
        print("Got a message", emailid)

        mail_file = tempfile.NamedTemporaryFile(dir=directory + folder + '/', delete=False)
        mail_file.write(data[0][1])
        mail_file.close()
        mail.store(emailid, '+FLAGS', '\\Deleted')


def main():
    """ Main function """

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__, help='print version')
    parser.add_argument('host', help='IMAP host')
    parser.add_argument('user', help='IMAP user')
    parser.add_argument('password', help='IMAP password')
    parser.add_argument('--spam-folder', default='spam', help='IMAP folder with spam, default to "spam"')
    parser.add_argument('--ham-folder', default='ham', help='IMAP folder with ham, defaults to "ham"')
    parser.add_argument('--directory', default='/tmp/sa-learn', help='work directory, defaults to "/tmp/sa-learn"')
    parser.add_argument('--sa-learn', default='/usr/bin/sa-learn', help='full path to sa-learn script, defaults to "/usr/bin/sa-learn"')
    args = parser.parse_args()

    args.directory = os.path.join(args.directory, '')  # add trailing slash if not there
    if os.path.exists(args.directory) and os.path.isdir(args.directory):
        if os.listdir(args.directory):
            print("ERROR: work directory is not empty, please clean up \"" + args.directory + "\" first")
            sys.exit(255)
    else:
        os.makedirs(args.directory, exist_ok=True)

    mail = imaplib.IMAP4(args.host)
    mail.starttls()
    mail.login(args.user, args.password)

    # Process Spam
    os.makedirs(args.directory + 'spam', exist_ok=True)
    resp, _dummy = mail.select(args.spam_folder)
    if resp == 'OK':
        print("Processing mail folder: ", args.spam_folder)
        process_mailbox(mail, 'spam', args.directory)
        for _dummy, _dummy, files in os.walk(args.directory + 'spam'):
            if files:
                os.system(args.sa_learn + " --spam" + " " + args.directory + 'spam')
    else:
        print("ERROR: Unable to open mailbox '" + args.spam_folder + "': ", resp)

    # Process Ham
    os.makedirs(args.directory + 'ham', exist_ok=True)
    resp, _dummy = mail.select(args.ham_folder)
    if resp == 'OK':
        print("Processing mail folder: ", args.ham_folder)
        process_mailbox(mail, 'ham', args.directory)
        for _dummy, _dummy, files in os.walk(args.directory + 'ham'):
            if files:
                os.system(args.sa_learn + " --ham" + " " + args.directory + 'ham')
    else:
        print("ERROR: Unable to open mailbox '" + args.ham_folder + "': ", resp)

    mail.expunge()
    mail.close()
    mail.logout()
    rmtree(args.directory)


if __name__ == "__main__":
    main()
