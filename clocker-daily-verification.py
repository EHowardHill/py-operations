import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pprint
import sqlalchemy as db

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_
from models import Event

from datetime import date, timedelta
from datetimerange import DateTimeRange

database = 'Frigg'
engine = db.create_engine('mysql+mysqlconnector://app:Collie12345!!@192.168.100.99:3306/'+database+'?charset=utf8')
Session = sessionmaker(bind=engine)
session = Session()

# Shift Killer
shifts = (
    session.query(Event)
        .filter(Event.CreatedAt.date() == date.today() - timedelta(days=1))
        .filter(Event.Comment == "%Machete%")
        )

# Shift Splitter

# Auto Adjuster
shifts = (
    session.query(Event)
        .filter(Event.CreatedAt.date() == date.today() - timedelta(days=1))
        .filter(Event.Adjuster == "auto-adjuster")
        )

# Calculator

# Daily Shift Summary Update

address_book = ['person1@company.com', 'person2@company.com', 'group3@company.com']
msg = MIMEMultipart()    
sender = 'me@company.com'
subject = "My subject"
body = "This is my email body"

msg['From'] = sender
msg['To'] = ','.join(address_book)
msg['Subject'] = subject
msg.attach(MIMEText(body, 'plain'))
text=msg.as_string()
s = smtplib.SMTP('our.exchangeserver.com')
s.sendmail(sender,address_book, text)
s.quit()