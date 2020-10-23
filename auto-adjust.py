import os, pprint, datetime, calendar, mysql.connector, logging

logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

mydb = mysql.connector.connect(
    host="192.168.100.99",
    user="app",
    password="Collie12345!!",
    database="Frigg",
    auth_plugin="mysql_native_password"
)
curs    = mydb.cursor()
now     = datetime.datetime.now()
q       = []

# Deduct from shift + one of the breaks

def adjust(id, value):

    std_bill_dur        = '0'
    std_payroll_dur     = '0'

    curs.execute('select Adjustment, Comment, Billable, Payable, std_hours_duration, graveyard_duration, CreatedAt from clocker_events where rec_id = ' + str(id) + ';')
    resp = curs.fetchone()

    if resp != None:
        curs.execute("update clocker_events set Adjustment = "  + str(value) +
                                    ", Comment = 'Excess Break', adjuster = 'Auto-Adjuster', adj_time = now(), adj_type = 0 " +
                                    "  where rec_id = "         + str(id) + ";")

 
# date_sub(curdate(), interval 7 day)

curs.execute("""
    select
        emp_id,
        -1 * round(sum(if(Event='BREAK', Event_Duration, 0)) - (30 * 60)),
        sum(if(Event='BREAK', Event_Duration, 0)),
        (30 * 60),
        1 as type
    from Frigg.clocker_events
    where
        date(UpdatedAt) = date_sub(curdate(), interval 1 day)
	group by 1
    having
        sum(if(Event_type='shift', Event_Duration, 0)) > (10 * 60 * 60) = 1
        and sum(if(Event='BREAK', Event_Duration, 0)) > (30 * 60) = 1
        
union

    select
        emp_id,
        -1 * (round(sum(if(Event='BREAK', Event_Duration, 0)) - (20 * 60))),
        sum(if(Event='BREAK', Event_Duration, 0)),
        (20 * 60),
        2 as type
    from Frigg.clocker_events
    where
        date(UpdatedAt) = date_sub(curdate(), interval 1 day)
	group by 1
    having
        sum(if(Event_type='shift', Event_Duration, 0)) > 6 * 60 * 60 = 1
        and sum(if(Event_type='shift', Event_Duration, 0)) < 10 * 60 * 60 = 1
        and sum(if(Event='BREAK', Event_Duration, 0)) > 20 * 60 = 1
        
union

    select
        emp_id,
        -1 * round(sum(if(Event='BREAK', Event_Duration, 0)) - (10 * 60)),
        sum(if(Event='BREAK', Event_Duration, 0)),
        (10 * 60),
        3 as type
    from Frigg.clocker_events
    where
        date(UpdatedAt) = date_sub(curdate(), interval 1 day)
	group by 1
    having
        sum(if(Event_type='shift', Event_Duration, 0)) < 6 * 60 * 60 = 1
        and sum(if(Event='BREAK', Event_Duration, 0)) > 10 * 60 = 1
""")
q += curs.fetchall()

for t in range(2):
    tv = []
    if q != []:
        for i in q:
            v = []
            curs.execute("""select
                                rec_id, emp_id
                            from Frigg.clocker_events
                            where
                                emp_id = '""" + i[0] + """'
                                and date(UpdatedAt) = date_sub(curdate(), interval 1 day)
                                and (Event_type = 'shift')
                            order by rec_id desc limit 1""")
            z = curs.fetchone()
            v += [z[0]]
            curs.execute("""select
                                rec_id
                            from Frigg.clocker_events
                            where
                                emp_id = '""" + i[0] + """'
                                and date(UpdatedAt) = date_sub(curdate(), interval 1 day)
                                and (Event = 'BREAK')
                            order by rec_id desc limit 1""")
            v += curs.fetchone()
            for vv in v:
                adjust(vv,i[1])
            tv += v

#except Exception as e:
#    logging.critical(str(e))
        
mydb.commit()
mydb.close()

mess = str(len(q)) + ' - total queries\n'
for v in tv:
    mess += ' - id - ' + str(v) + ' modified\n'
mess += '\n'
print(mess)

logging.info(mess)

# database
# date of work