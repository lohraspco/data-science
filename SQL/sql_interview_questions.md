
- <details><summary>Workers With The Highest Salaries</summary>
table worker
worker_id: int64 
first_name: object 
last_name: object 
salary: int64 
joining_date: datetime64[ns] 
department: object 
table title
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


</details>

- <details><summary>Distances Traveled</summary>
Find the top 10 users that have traveled the greatest distance. Output their id, name and a total distance traveled.

     - table lyft_rides_log
| id    | user\_id | distance |
| ----- | -------- | -------- |
| int64 | int64    | int64    |

     - table lyft_users
| id    | name | 
| ----- | -------- | 
| int64 | object    | 

```sql
select a.name, b.distance  from  lyft_users a
inner join (
select user_id, distance from lyft_rides_log order by distance desc limit 10) b
on  b.user_id = a.id
order by b.distance desc
```
</details>

- <details><summary>3rd Most Reported Health Issues</summary>


| activity\_date:  | employee\_id: | facility\_address: | facility\_city: | facility\_id: | facility\_name: | facility\_state: | facility\_zip: | grade: | owner\_id: | owner\_name: | pe\_description: | program\_element\_pe: | program\_name: | program\_status: | record\_id: | score: | serial\_number: | service\_code: | service\_description: |
| ---------------- | ------------- | ------------------ | --------------- | ------------- | --------------- | ---------------- | -------------- | ------ | ---------- | ------------ | ---------------- | --------------------- | -------------- | ---------------- | ----------- | ------ | --------------- | -------------- | --------------------- |
| datetime64\[ns\] | object        | object             | object          | object        | object          | object           | object         | object | object     | object       | object           | int64                 | object         | object           | object      | int64  | object          | int64          | object                |
     - Detail 2.1
     - Detail 2.2

```sql
select a.name, b.distance  from  lyft_users a
inner join (
select user_id, distance from lyft_rides_log order by distance desc limit 10) b
on  b.user_id = a.id
order by b.distance desc
```


</details>