
# SQL codes and tips
Here is a link to the SQL interview questions which includes very useful short guide to SQL.
https://www.stratascratch.com/blog/sql-interview-questions-you-must-prepare-the-ultimate-guide/

Basic SQ 
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


# Window Functions:

What are window functions in SQL, and how do they differ from aggregate functions?
1. Scope:

Aggregate Functions: Collapse multiple rows into a single summary row (e.g., SUM(), AVG(), COUNT()).

Window Functions: Perform calculations across a "window" of rows without collapsing the result set (e.g., ROW_NUMBER(), RANK(), LEAD(), LAG()).

2. Usage:

Aggregate Functions: Often used with GROUP BY to summarize data.

Window Functions: Used with the OVER() clause to define the window.

Write a query to calculate the running (rolling) total of rental amounts for each customer.
~~~sql
select customer_id, amount, 
    sum(amount) over (partition by customer_id order by payment_date) as runnint_total
from payment;
~~~


# Where VS Having 
- WHERE Clause:
Purpose: Filters rows before any grouping or aggregation takes place.
Usage: Used with SELECT, UPDATE, DELETE statements
Conditions: Can include conditions on individual columns or expressions.
~~~sql
SELECT customer_id, amount
FROM payment
WHERE amount > 50
~~~
- HAVING Clause:
Purpose: Filters groups of rows after grouping and aggregation.
Usage: Used with GROUP BY to filter groups based on aggregate functions.
Conditions: Can include conditions on aggregate expressions like SUM(), COUNT(), AVG(), etc.
~~~sql
SELECT customer_id, SUM(amount) AS total_amount
FROM payment
GROUP BY customer_id
HAVING SUM(amount) > 500;
~~~
