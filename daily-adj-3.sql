update Frigg.clocker_events main
inner join
(
	select
		rec_id,
		-1 * (round(sum(if(Event='BREAK', Event_Duration + ifnull(Adjustment,0), 0)) - (10 * 60))) as x
	from Frigg.clocker_events
	where
		date(UpdatedAt) = date_sub(curdate(), interval 1 day)
	group by 1
	having
		sum(if(Event_type='shift', Event_Duration, 0)) < 6 * 60 * 60 = 1
		and sum(if(Event='BREAK', Event_Duration + ifnull(Adjustment,0), 0)) > 10 * 60 = 1
) sec
on sec.rec_id = main.rec_id
set
	main.Adjustment = rec_id.x,
	main.adjuster = 'Auto-Adjuster',
    main.adj_time = now(),
    main.adj_type = 0,
    main.Comment = 'Excess Break'