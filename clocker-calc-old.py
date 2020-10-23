import os, mysql.connector, pprint, logging, datetime

logging.basicConfig(filename='clocker-calc.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.INFO)

# Open database connection
mydb = mysql.connector.connect(
    host="192.168.100.99",
    user="app",
    password="Collie12345!!",
    database="Frigg",
    auth_plugin="mysql_native_password"
)
curs = mydb.cursor()

now     = datetime.datetime.now()
mess    = str(now) + '\n'

try:
	curs.execute("""
	update
		Frigg.clocker_events scope
	inner join (
		select
			rec_id,
			first,
			second,
			
			-- Default activity out value calculations
			if(first < 0, 0, if(Billable = 'FALSE', first * -1, first)) as std_bill_dur,
			if(second < 0, 0, if(Billable = 'FALSE', second * -1, second)) as grav_bill_duration,
			if(first < 0, 0, if(Payable = 'FALSE', first * -1, first)) as std_payroll_dur,
			if(second < 0, 0, if(Payable = 'FALSE', second * -1, second)) as grav_payroll_dur
		from
		(
			select
				rec_id,
				Billable,
				Payable,

				-- Dispose of data if over or under the limit
				if(first<0 or first>50400,0,first) as first,
				if(second<0 or second>50400,0,second) as second
			from (
			select
				rec_id,
				Billable,
				Payable,

				-- Shift duration during the day
				timestampdiff(
					second,
					if(
						hour(CreatedAt) >= 6 and hour(CreatedAt) < 22,
						CreatedAt,
						if(
							hour(updatedAt) >= 22,
							date_add(date(CreatedAt), interval 22 hour),
							if (
								hour(updatedAt) >= 6,
								date_add(date(CreatedAt), interval 6 hour),
								date_add(date(CreatedAt), interval 22 hour)
							)
						)
					),
					if(
							hour(updatedAt) >= 6 and hour(updatedAt) < 22,
							updatedAt,
							if(
								hour(CreatedAt) < 22,
								date_add(date(updatedAt), interval 22 hour),
								if (
									hour(CreatedAt) < 6,
									date_add(date(updatedAt), interval 6 hour),
									date_add(date(updatedAt), interval 22 hour)
								)
							)
						)
				) as first,

				-- Shift duration during graveyard hours
				timestampdiff(
					second,
					if(
						hour(CreatedAt) < 6 or hour(CreatedAt) >= 22,
						CreatedAt,
						if(
							hour(updatedAt) < 22,
							date_add(date(CreatedAt), interval 22 hour),
							if (
								hour(updatedAt) < 6,
								date_add(date(CreatedAt), interval 6 hour),
								date_add(date(CreatedAt), interval 22 hour)
							)
						)
					),
					if(
						hour(updatedAt) < 6 or hour(updatedAt) >= 22,
						updatedAt,
						if(
							hour(CreatedAt) >= 22,
							date_add(date(updatedAt), interval 22 hour),
							if (
								hour(CreatedAt) >= 6,
								date_add(date(updatedAt), interval 6 hour),
								date_add(date(updatedAt), interval 22 hour)
							)
						)
					)
				) as second
			from Frigg.clocker_events
			where std_hours_duration is null and date(CreatedAt) >= curdate() - 2
			group by rec_id
			) calculation
		) results
	) results_adjusted
	on results_adjusted.rec_id = scope.rec_id
	set
		scope.std_hours_duration = first,
		scope.graveyard_duration = second,

		-- Account for adjustment values
		scope.std_bill_dur =
			if(scope.adj_type=0,results_adjusted.std_bill_dur+if(results_adjusted.std_bill_dur<0,Adjustment*-1,Adjustment),results_adjusted.std_bill_dur),
		scope.grav_bill_duration =
			if(scope.adj_type=1,results_adjusted.grav_bill_duration+if(results_adjusted.grav_bill_duration<0,Adjustment*-1,Adjustment),results_adjusted.grav_bill_duration),
		scope.std_payroll_dur =
			if(scope.adj_type=0,results_adjusted.std_payroll_dur+if(results_adjusted.std_payroll_dur<0,Adjustment*-1,Adjustment),results_adjusted.std_payroll_dur),
		scope.grav_payroll_dur =
			if(scope.adj_type=1,results_adjusted.grav_payroll_dur+if(results_adjusted.grav_payroll_dur<0,Adjustment*-1,Adjustment),results_adjusted.grav_payroll_dur)
	""")

	mydb.commit()
	mess += '- program successful'

except Exception as e:
	mess += '- program failed because of the following exception: ' + str(e)

mydb.close()

print(mess)
logging.info(mess)