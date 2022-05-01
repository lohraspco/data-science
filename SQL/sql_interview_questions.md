
In some of the examples in this section we use the DVD rental data. 
Please refer to the following link as the source of the questions: 
https://platform.stratascratch.com/coding

<details><summary>Workers With The Highest Salaries</summary>


     - table worker
| worker\_id | first\_name | last\_name | salary | joining\_date    | department | table | worker\_ref\_id | worker\_title | affected\_from   |
| ---------- | ----------- | ---------- | ------ | ---------------- | ---------- | ----- | --------------- | ------------- | ---------------- |
| int64      | object      | object     | int64  | datetime64\[ns\] | object     | title | int64           | object        | datetime64\[ns\] |

```sql

select worker_title from title t
inner join (
    select * from worker where salary = (select max(salary) from worker)
) w2
on t.worker_ref_id = w2.worker_id
```


</details>

<details><summary>Distances Traveled</summary>
Find the top 10 users that have traveled the greatest distance. Output their id, name and a total distance traveled.

     - table lyft_rides_log
| id    | user\_id | distance |
| ----- | -------- | -------- |
| int64 | int64    | int64    |

     - table lyft_users
| id    | name   |
| ----- | ------ |
| int64 | object |

```sql
select a.name, b.distance  from  lyft_users a
inner join (
select user_id, distance from lyft_rides_log order by distance desc limit 10) b
on  b.user_id = a.id
order by b.distance desc
```
</details>

<details><summary>3rd Most Reported Health Issues</summary>

Each record in the table is a reported health issue and its classification is categorized by the facility type, size, risk score which is found in the pe_description column.

If we limit the table to only include businesses with Cafe, Tea, or Juice in the name, which businesses belong to the categories (pe_descriptions) tying for third in overall inspections? Output the name of the facilities found in the facility_name column.

| activity\_date:  | employee\_id: | facility\_address: | facility\_city: | facility\_id: | facility\_name: | facility\_state: | facility\_zip: | grade: | owner\_id: | owner\_name: | pe\_description: | program\_element\_pe: | program\_name: | program\_status: | record\_id: | score: | serial\_number: | service\_code: | service\_description: |
| ---------------- | ------------- | ------------------ | --------------- | ------------- | --------------- | ---------------- | -------------- | ------ | ---------- | ------------ | ---------------- | --------------------- | -------------- | ---------------- | ----------- | ------ | --------------- | -------------- | --------------------- |
| datetime64\[ns\] | object        | object             | object          | object        | object          | object           | object         | object | object     | object       | object           | int64                 | object         | object           | object      | int64  | object          | int64          | object                |
     - Detail 2.1
     - Detail 2.2

```sql
with selected_restaurants as (
	select la.facility_name,la.pe_description, la.record_id from saffron.los_angeles_restaurant_health_inspections la 
	where la.facility_name like '%CAFE%' or la.facility_name like '%TEA%' or la.facility_name like '%JUICE%'),
 top_third_issues as (
	select re.pe_description ,count(re.record_id) as n_issues
	from selected_restaurants re
	group by re.pe_description 
	order by n_issues desc
	limit 3
	),
third_issu as (
	select * from top_third_issues where n_issues= (select min(n_issues) from top_third_issues)
	)
select facility_name from selected_restaurants rr
join third_issu tt using (pe_description)

```


</details>

<details><summary>Films with Most Payment</summary>
Select the films with Most Payment

```sql
select title from film 
join
(  
     select film_id from inventory 
     join  
     (
          select inventory_id from rental
          join 
          (
               select * from payment 
               where amount = (select max(amount) from payment)
          ) maxP 
 	     on rental.rental_id = maxP.rental_id
 	) maxInv
     on maxInv.inventory_id = inventory.inventory_id
) selecte_films

on selecte_films.film_id = film.film_id

```
</details>


<details><summary>count number of drama movies</summary>
```sql
select count(*)  
from film
inner join film_category using(film_id)
inner join category using(category_id)
where category_id = 7
```

</details>


<details><summary>Average rating per category</summary>
```sql
select category_id , avg(rental_Rate)  
from film
inner join film_category using (film_id)
inner join category using(category_id)
group by category_id
```

</details>


select * from (select date, ticker, high, 
 			   dense_rank() over (order by high desc) r 
			   from saffron.daily_price
			  where ticker like 'A%' and ticker like '%E') s
where r=3
			   