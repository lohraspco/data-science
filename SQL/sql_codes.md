/*markdown
Some SQL tips
*/

/*markdown
```sql
select date, ticker, -ROUND(close) as closenegative, round(high*2) as twohight from saffron.daily_price limit 2

select date, ticker, round(open), ROUND(close) as closenegative, round(high*2) as twohight from saffron.daily_price where close <open limit 2 

select date, ticker, cast(open as int)+ cast(close as int) as sumOC from saffron.daily_price where sumOC > 200 limit 2
```

note that we cannot use "" for the strings

```sql
select d.date, d.ticker, d.sumOC from 
    (select date, ticker, cast(open as int)+ cast(close as int) as sumOC
    from saffron.daily_price ) as d 
where d.sumOC between 260 and 300 and d.date <> '2018-04-25T00:00:00.000Z' and ticker is not NULL and ticker in ('A','F', 'FB')  limit 2
```
```sql
select date, ticker, open from saffron.daily_price where ticker like 'AB%' order by close limit 2

select date, ticker, open from saffron.daily_price where ticker like 'AB%' order by close limit 2
```


# Workers With The Highest Salaries
## table worker
worker_id: int64 
first_name: object 
last_name: object 
salary: int64 
joining_date: datetime64[ns] 
department: object 
## table title
worker_ref_id: int64 
worker_title: object 
affected_from: datetime64[ns] 

```sql

select worker_title from title t
inner join (
    select * from worker where salary = (select max(salary) from worker)
) w2
on t.worker_ref_id = w2.worker_id
```

# Distances Traveled
Find the top 10 users that have traveled the greatest distance. Output their id, name and a total distance traveled.

## table lyft_rides_log
id: int64 user_id: int64 distance: int64
## table lyft_users
id: int64 name: object
```sql
select a.name, b.distance  from  lyft_users a
inner join (
select user_id, distance from lyft_rides_log order by distance desc limit 10) b
on  b.user_id = a.id
order by b.distance desc
```