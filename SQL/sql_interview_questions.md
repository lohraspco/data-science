
In some of the examples in this section we use the DVD rental data. 
Please refer to the following link as the source of the questions: 
https://platform.stratascratch.com/coding




# FAANG Interview Questions
<details><summary>least responsive" companies</summary>

-- To determine the "least responsive" companies, we first need to define responsiveness. Based on the request lifecycle, here’s a reasonable interpretation:
~~~sql
WITH status_pairs AS (
    SELECT 
        r1.request_id,
        r1.company_id,
        r1.timestamp AS start_time,
        r2.timestamp AS end_time
    FROM request_status_logs r1
    JOIN request_status_logs r2 
      ON r1.request_id = r2.request_id 
     AND r1.timestamp < r2.timestamp
    WHERE r1.request_status = 'awaiting_company_response'
    -- Ensure r2 is the next status after awaiting_company_response
      AND NOT EXISTS (
            SELECT 1 FROM request_status_logs r3
            WHERE r3.request_id = r1.request_id
              AND r3.timestamp > r1.timestamp 
              AND r3.timestamp < r2.timestamp
        )
)

SELECT 
    c.company_name,
    COUNT(DISTINCT sp.request_id) AS num_requests,
    ROUND(
~~~
</details>
<details><summary>users active for 3 consecutive days</summary>

-- Find all the users who were active for 3 consecutive days or more.


~~~sql
with activity_with_lag as (
select *,
row_number() over (partition by user_id order by activity_date) as rn,
	activity_date - interval '1 day' * row_number() over (partition by user_id order by activity_date) as grp
from activity
)
select user_id, grp, count(*) as streak_length
from activity_with_lag
group by user_id, grp
having count(*)>2
~~~
</details>

<details><summary>Customer Tracking</summary>

Given the users' sessions logs on a particular day, calculate how many hours each user was active that day.

~~~sql
with sessions as (
select l.cust_id, l.timestamp as t1, l.state as s1, r.timestamp as t2, (r.timestamp - l.timestamp)/3600 as sess_time
from cust_tracking l
join cust_tracking r on l.cust_id = r.cust_id and  l.timestamp<r.timestamp and l.state=1 and r.state=0
where not exists (select 1 from cust_tracking ct where ct.cust_id = l.cust_id and ct.timestamp >l.timestamp and ct.timestamp<r.timestamp)
)

select cust_id, sum(sess_time) from sessions
group by cust_id;
~~~


</details>


# My Practices
<details><summary>Common Table Expressions (CTEs)</summary>


Explain the difference between a CTE and a subquery.
- Scope and Readability:CTEs are defined at the beginning of the query, making the query easier to read and understand.
- Reusability:CTEs can be referenced multiple times in the same query, whereas subqueries cannot.
- Recursion: CTEs can be recursive, allowing for more complex operations like hierarchical queries. Subqueries do not support recursion.

Write a recursive CTE to find all the films rented by a specific customer, including the rental dates.
</details>

<details><summary>questions</summary>
# Joins:

What is the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL JOIN?

Write a query to find customers who have rented films from both the "Action" and "Comedy" categories.

Subqueries:

What is a correlated subquery, and how does it differ from a regular subquery?

Write a query to find the top 5 customers with the highest total rental amounts using a subquery.

Indexes:

What are the different types of indexes in SQL, and when should you use them?

How would you optimize a query that retrieves the most frequently rented films?

Performance Tuning:

What are some common techniques for optimizing SQL queries?

Write a query to identify and remove duplicate rows from the rental table.

Advanced Aggregations:

Explain the GROUP BY clause and the HAVING clause. How do they differ?

Write a query to calculate the average rental duration for each film category.

Data Manipulation:

How do you handle NULL values in SQL? Provide examples.

Write a query to update the rental rate of all films in the "Drama" category by increasing it by 10%.

Transactions and Concurrency:

What are transactions in SQL, and why are they important?

Explain the different isolation levels in SQL and their impact on data consistency.

Advanced Query Techniques:

Write a query to find the second highest rental amount for each customer.

How would you implement pagination in SQL to retrieve a specific range of rows?

select * from (select date, ticker, high, 
 			   dense_rank() over (order by high desc) r 
			   from saffron.daily_price
			  where ticker like 'A%' and ticker like '%E') s
where r=3
			   

-- List all customers who live in California.
select c.first_name, c.last_name from customer c
left join address a on c.address_id = a.address_id 
left join city ci on ci.city_id = a.city_id
left join country co on co.country_id = ci.country_id
where country='China';



-- Which films are rated ‘PG’ and have a rental duration greater than 5 days?
select * from film where rating='PG' and rental_duration>5;

-- Find the total number of films in each category.
select count(f.film_id), c.category_id, cn.name
from film f
left join film_category c
on f.film_id = f.film_id
left join category cn on cn.category_id = c.category_id
group by c.category_id, cn.name;


-- List all films that have never been rented.
select f.title, f.film_id from film f
left join inventory i on i.film_id = f.film_id
left join rental r on r.inventory_id = i.inventory_id
group by f.film_id
having count(r.rental_id)=0;

-- Another common and very efficient way to get the same result is by using NOT EXISTS. This can sometimes be faster as it can stop checking for a film as soon as it finds the first rental record.

SELECT   f.title,   f.film_id
FROM   film AS f
WHERE   NOT EXISTS (
    SELECT       1 -- Using 1 is a convention, as we only care if a row exists, not what's in it.
    FROM       inventory AS i
      JOIN rental AS r ON i.inventory_id = r.inventory_id
    WHERE       i.film_id = f.film_id
  );



-- Get the names and emails of customers who rented a film in January 2006.
select distinct c.first_name, c.last_name 
from rental r
left join customer c on c.customer_id = r.customer_id
where r.rental_date>='2005-08-01'  and  r.rental_date<'2005-09-01'
limit 2;


-- Which customers have rented more than 10 films?
select c.first_name, count(c.customer_id)
from customer c
left join rental r
on r.customer_id = c.customer_id
group by r.customer_id, c.first_name
having count(*)>10;

-- Find the top 5 most rented films.
select f.title, count(f.film_id) from film f
join inventory i on i.film_id = f.film_id
join rental r on r.inventory_id = i.inventory_id
group by f.film_id
order by  count(r.rental_id) desc
limit 5;

-- What is the average rental duration per film category?



-- List the top 3 cities by revenue generated.
select ci.city, sum(p.amount) from city ci 
join address a on ci.city_id=a.city_id
join customer c on c.address_id=a.address_id
join rental r on r.customer_id=c.customer_id
join payment p on p.rental_id=r.rental_id
group by ci.city_id
order by sum(p.amount) desc
limit 3;


-- Find the revenue generated by each staff member.


-- For each customer, find their first rental date.
select customer_id , min(rental_date) from rental
group by customer_id ;


-- approach 2
with CustomerRankedRental as (select customer_id, rental_date,
								ROW_NUMBER() over (partition by customer_id order by rental_date desc) as rd
								from rental)
select customer_id, rental_date as first_rental_date from CustomerRankedRental
where rd=1;


-- List the top 3 customers by total payment amount.
select customer_id, sum(amount) as total
from payment 
group by customer_id
order by total desc
limit 3;

-- Show the running total of payments made by customer ‘Mary Smith’.
select 
	p.customer_id,
	sum(p.amount) over (order by payment_date) 
from  payment p
where customer_id in (select customer_id from customer where first_name='Mary' and last_name='Smith' );


-- Identify which hour of the day gets the most rentals.
select extract(hour from rental_date) as h, count(*) as num  from rental
group by h
order by num desc
limit 1;


-- Create a cohort of customers who rented in their first month and analyze their retention.

with customer_month as (
		select customer_id,    
		EXTRACT(YEAR FROM create_date)::text || '-' || LPAD(EXTRACT(MONTH FROM create_date)::text, 2, '0') AS create_mon,
		last_update from customer), 
rental_month as( 
			select customer_id,
			extract(year from rental_date)::text || '-' || LPAD(extract(month from rental_date)::text,2,'0') as tm 
			from rental)

select c.customer_id, c.create_mon 
from customer_month c
inner join rental_month  r
on r.customer_id = c.customer_id and r.tm=c.create_mon;



-- Create a cohort of customers who rented in their first month and analyze their retention.


</details>

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

AVG(EXTRACT(EPOCH FROM (sp.end_time - sp.start_time)) / 3600), 2) AS avg_hours_awaiting_response
FROM status_pairs sp
JOIN companies c ON sp.company_id = c.company_id
GROUP BY c.company_name
ORDER BY avg_hours_awaiting_response DESC
LIMIT n;
