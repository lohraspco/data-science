
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

- <details><summary>Detail 1</summary>

     - Detail 1.1
     - Detail 1.2

- <details><summary>Detail 2</summary>

     - Detail 2.1
     - Detail 2.2

</details>
</details>