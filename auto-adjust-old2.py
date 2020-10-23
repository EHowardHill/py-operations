import os, pprint, datetime, calendar, mysql.connector, logging

logging.basicConfig(filename='auto-adjust.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

mydb = mysql.connector.connect(
    host="192.168.100.99",
    user="app",
    password="Collie12345!!",
    database="Frigg",
    auth_plugin="mysql_native_password"
)
curs    = mydb.cursor()
now     = datetime.datetime.now()
mess    = str(now) + '\n'

# Deduct from shift + one of the breaks

try:
    curs.execute(
        """
        update Frigg.clocker_events main
        inner join
        (
            select
                rec_id,
                x,
                (select rec_id from Frigg.clocker_events where emp_id = a.emp_id and Event = 'shift' and date(UpdatedAt) = a.d_a order by rec_id desc limit 1) as shift_id
            from
            (
                select
                    rec_id,
                    emp_id,
                    date(UpdatedAt) as d_a,
                    -1 * (round(sum(if(Event='BREAK', Event_Duration, 0)) - (10 * 60))) as x
                from Frigg.clocker_events
                where
                    date(UpdatedAt) >= date_sub(curdate(), interval 7 day)
                    and Event = 'break'
                group by d_a, emp_id
                having
                    sum(if(Event_type='shift', Event_Duration, 0)) < 6 * 60 * 60 = 1
                    and sum(if(Event='BREAK', Event_Duration, 0)) > 10 * 60 = 1
            ) a
        ) sec
        on sec.rec_id = main.rec_id or sec.shift_id = main.rec_id
        set
            main.Adjustment = sec.x,
            main.adjuster = 'Auto-Adjuster',
            main.adj_time = now(),
            main.adj_type = 0,
            main.Comment = 'Excess Break'
        """
    )
    mess += '- query 3 executed\n'
    mydb.commit()

    curs.execute(
        """
        update Frigg.clocker_events main
        inner join
        (
            select
                rec_id,
                x,
                (select rec_id from Frigg.clocker_events where emp_id = a.emp_id and Event = 'shift' and date(UpdatedAt) = a.d_a order by rec_id desc limit 1) as shift_id
            from
            (
                select
                    rec_id,
                    emp_id,
                    date(UpdatedAt) as d_a,
                    -1 * (round(sum(if(Event='BREAK', Event_Duration, 0)) - (20 * 60))) as x
                from Frigg.clocker_events
                where
                    date(UpdatedAt) >= date_sub(curdate(), interval 7 day)
                    and Event = 'break'
                group by d_a, emp_id
                having
                    sum(if(Event_type='shift', Event_Duration, 0)) > 6 * 60 * 60 = 1
                    and sum(if(Event_type='shift', Event_Duration, 0)) < 10 * 60 * 60 = 1
                    and sum(if(Event='BREAK', Event_Duration, 0)) > 20 * 60 = 1
            ) a
        ) sec
        on sec.rec_id = main.rec_id or sec.shift_id = main.rec_id
        set
            main.Adjustment = sec.x,
            main.adjuster = 'Auto-Adjuster',
            main.adj_time = now(),
            main.adj_type = 0,
            main.Comment = 'Excess Break'
        """
    )
    mess += '- query 2 executed\n'
    mydb.commit()

    curs.execute(
        """
        update Frigg.clocker_events main
        inner join
        (
            select
                rec_id,
                x,
                (select rec_id from Frigg.clocker_events where emp_id = a.emp_id and Event = 'shift' and date(UpdatedAt) = a.d_a order by rec_id desc limit 1) as shift_id
            from
            (
                select
                    rec_id,
                    emp_id,
                    date(UpdatedAt) as d_a,
                    -1 * (round(sum(if(Event='BREAK', Event_Duration, 0)) - (30 * 60))) as x
                from Frigg.clocker_events
                where
                    date(UpdatedAt) >= date_sub(curdate(), interval 7 day)
                    and Event = 'break'
                group by d_a, emp_id
                having
                    sum(if(Event_type='shift', Event_Duration, 0)) > (10 * 60 * 60) = 1
                    and sum(if(Event='BREAK', Event_Duration, 0)) > (30 * 60) = 1
            ) a
        ) sec
        on sec.rec_id = main.rec_id or sec.shift_id = main.rec_id
        set
            main.Adjustment = sec.x,
            main.adjuster = 'Auto-Adjuster',
            main.adj_time = now(),
            main.adj_type = 0,
            main.Comment = 'Excess Break'
        """
    )
    mess += '- query 1 executed\n'
    mydb.commit()

    mydb.close()
    print(mess)

except Exception as e:
    mess = str(e)

logging.info(mess)

# database
# date of work