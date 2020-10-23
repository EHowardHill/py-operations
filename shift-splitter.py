import os, pprint, datetime, calendar, mysql.connector, logging

logging.basicConfig(filename='shift-splitter.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

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

#try:
if True:
    # Find all employees
    curs.execute("select distinct(emp_id) from Frigg.clocker_events where UpdatedAt is null")
    d = curs.fetchall()

    # End all of yesterday's breaks
    curs.execute(
        """
        update
        Frigg.clocker_events
        set
            UpdatedAt = date_sub(curdate(), interval 1 second),
            Event_end_time = date_sub(curdate(), interval 1 second),
            Event_Duration = timestampdiff(second, CreatedAt, date_sub(curdate(), interval 1 second))
        where UpdatedAt is null and emp_id is not null;
        """
    )
    mydb.commit()

    # create new shift 
    for user in d:
        user = user[0]
        curs.execute("select LOB, Team, Campaign, Location, Role from Frigg.Employee_Mast where EmpID = '" + user + "';")
        args = curs.fetchone()
        if args != []:
            lob = 'NOT FOUND' if args[0] == None else args[0]
            team = 'NOT FOUND' if args[1] == None else args[1]
            camp = 'NOT FOUND' if args[2] == None else args[2]
            location = 'NOT FOUND' if args[3] == None else args[3]
            role = 'NOT FOUND' if args[4] == None else args[4]
        else:
            lob = 'NOT FOUND'
            team = 'NOT FOUND'

        curs.execute(
            'insert into Frigg.clocker_events ' +
            '(emp_id, CreatedAt, Event, Comment, ' + 
            'Event_type, Event_start_time, Campaign_Name, ' + 
            'Lob, Team, Site_Location, Billable, Payable, ' +
            'Role, Scheduled_Duration) ' +
            'values (%s,date_add(curdate(),interval 1 second),%s,%s,%s,date_add(curdate(),interval 1 second),%s,%s,%s,%s,%s,%s,%s,%s)',
            [
                user,
                'shift',
                'shift splitter',
                'shift',
                camp,
                lob,
                team,
                location,
                'TRUE',
                'TRUE',
                role,
                510
            ]
            )

    mess += '- shift splitting executed\n'
            
    mydb.commit()
    mydb.close()

    for i in d:
        mess += str(i) + '\n'
    print(mess)

try:
	pass
except Exception as e:
    mess = str(e)

print(mess)
logging.info(mess)

# database
# date of work
