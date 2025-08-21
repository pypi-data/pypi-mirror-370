"""
notification.py
$Id: notification.py 2452 2020-04-23 19:20:47Z pe $

General notification / alert handling.
Collects messages and sends emails with collected messages at demand.
As a fallback (mail sending problems) notifications will be written to logfile.

History:
V.1.0.0  2013-06-26  pe  initial

"""

import smtplib
import socket
import logging

class NotificationDeliveryError(Exception):
    """
    Exception raised on email delivery errors.
    """
    pass

class Notification(object): # pylint: disable=R0902
    # R0902: Too many instance attributes
    """
    Class for keeping info on all notification during the processing of one
    file.
    """
    def __init__(self, smtp, sender="", fromname="", recipients=None,
                 bcc=None, subject=None, headertext='', trailertext='',
                 override_recipients=None, parentlogger=logging.getLogger()):
        # pylint: disable=R0913
        # R0913: Too many arguments
        """
        Set up notification object.
        """
        self.messages = []
        self.smtp = smtp
        self.sender = sender
        self.fromname = fromname
        if isinstance(recipients, (list, tuple)):
            self.recipients = list(recipients)
        elif  recipients:
            self.recipients = [recipients]
        else:
            self.recipients = []
        if isinstance(bcc, (list, tuple)):
            self.bcc = list(bcc)
        elif  bcc:
            self.bcc = [bcc]
        else:
            self.bcc = []
        if isinstance(override_recipients, (list, tuple)):
            self.override_recipients = list(override_recipients)
        elif  override_recipients:
            self.override_recipients = [override_recipients]
        else:
            self.override_recipients = []
        self.subject = subject
        self.headertext = headertext
        self.trailertext = trailertext
        self.logger = parentlogger.getChild('notifications')

    def add(self, message):
        """
        Add a message to the data submitter(s).
        """
        self.messages.append(message)

    def send(self):
        """
        Send all pending notifications.
        """
        if not self.messages:
            return
        self.logger.info("sending pending notification email")

        try:
            smtp = smtplib.SMTP(self.smtp, timeout=5)
        except (socket.error, socket.timeout, socket.gaierror,
                smtplib.SMTPConnectError) as expt:
            errtxt = "error connecting to mailserver " + self.smtp
            errtxt += "; " + str(expt)
            raise NotificationDeliveryError(errtxt)

        msg = self.generate_body()
        if self.override_recipients:
            rec = self.override_recipients
        else:
            rec = self.recipients + self.bcc

        try:
            smtp.sendmail(self.sender, rec, msg)
        except (smtplib.SMTPHeloError, smtplib.SMTPRecipientsRefused,
                smtplib.SMTPSenderRefused, smtplib.SMTPDataError) as expt:
            errtxt = "send email failed; {}: {}".format(expt.__class__.__name__,
                                                        str(expt))
            self.logger.error(errtxt)
            raise NotificationDeliveryError(errtxt)
        smtp.quit()

    def generate_body(self):
        """
        Generate email body.
        Parameters:
            None
        Returns:
            None
        """
        msg = "From: {} <{}>\r\n".format(self.fromname, self.sender) +\
              "To: {0}\r\n".format(", ".join(self.recipients)) +\
              "Subject: {}\r\n\r\n".format(self.subject) +\
              self.headertext +\
              '\r\n'.join(self.messages) +\
              self.trailertext
        if self.override_recipients:
            msg = "From: {} <{}>\r\n".format(self.fromname, self.sender) +\
                  "To: {0}\r\n".format(", ".join(self.override_recipients)) +\
                  "Subject: {}\r\n\r\n".format(self.subject) +\
                  "Email Notification - " +\
                  "Addressee overwritten\r\n\r\n" +\
                  "=== original email follows ===\r\n\r\n" +\
                  msg
        return msg
