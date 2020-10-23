import pprint
import sqlalchemy as db

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from datetimerange import DateTimeRange

database = 'Frigg'
engine = db.create_engine('mysql+mysqlconnector://app:Collie12345!!@192.168.100.99:3306/'+database+'?charset=utf8')
Session = sessionmaker(bind=engine)
session = Session()

from models import Event

q = (
        session.query(Event)
        #.filter_by(std_hours_duration=None)
        .filter(Event.CreatedAt >= datetime.today() - timedelta(days=2))
        .filter(Event.CreatedAt < datetime.today() - timedelta(days=1))
        .filter(Event.UpdatedAt != None)
        .filter(or_(Event.std_hours_duration == None, Event.graveyard_duration == None))
        .group_by(Event.rec_id)
        .all()
        )

for qq in q:

    try:
        # Set up date ranges
        dur = qq.Event_Duration
        act_range = DateTimeRange(qq.CreatedAt, qq.UpdatedAt)
        std_range = DateTimeRange(
            datetime(qq.CreatedAt.year, qq.CreatedAt.month, qq.CreatedAt.day) + timedelta(hours=6),
            datetime(qq.CreatedAt.year, qq.CreatedAt.month, qq.CreatedAt.day) + timedelta(hours=22))

        # Split STANDARD and GRAVEYARD
        try:
            std = act_range.intersection(std_range).timedelta.total_seconds()
            grv = dur - std
            if grv == 1:
                grv -= 1
                std += 1
            if std + grv != dur:
                if std > grv:
                    std += dur - std - grv
                else:
                    grv += dur - grv - std
        except:
            std = 0
            grv = dur

        #pprint.pprint([std,grv,dur])

        # Configure pre-adjustment
        qq.std_hours_duration   = std
        qq.graveyard_duration   = grv

        # Adjustment consideration
        if qq.Adj_Type == 0:    std += qq.Adjustment if std > 0 else qq.Adjustment * -1
        if qq.Adj_Type == 1:    grv += qq.Adjustment if grv > 0 else qq.Adjustment * -1

        # Separation into various fields
        qq.std_bill_dur         = std if qq.Billable.upper()    == 'TRUE' else std * -1
        qq.grav_bill_duration   = grv if qq.Billable.upper()    == 'TRUE' else grv * -1
        qq.std_payroll_dur      = std if qq.Payable.upper()     == 'TRUE' else std * -1
        qq.grav_payroll_dur     = grv if qq.Payable.upper()     == 'TRUE' else grv * -1

        #s = 'select CreatedAt, UpdatedAt, Billable, Payable, Event_Duration, adj_type, Adjustment, ' + str(qq.std_bill_dur) + ' as std_bill_dur, ' + str(qq.grav_bill_duration) + ' as grav_bill_duration, ' + str(qq.std_payroll_duration) + ' as std_payroll_duration, ' + str(qq.grav_payroll_dur) + ' as grav_payroll_dur from Frigg.clocker_events where rec_id = ' + str(qq.rec_id) + ';'
        s = qq.rec_id
        print(s)

        session.commit()

    except:
        try:
            print(qq.rec_id)
        except:
            print("No ID!")