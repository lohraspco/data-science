/*markdown
Some SQL tips
*/



select date, ticker, -ROUND(close) as closenegative, round(high*2) as twohight from saffron.daily_price limit 2

select date, ticker, round(open), ROUND(close) as closenegative, round(high*2) as twohight from saffron.daily_price where close <open limit 2 

select date, ticker, cast(open as int)+ cast(close as int) as sumOC from saffron.daily_price where sumOC > 200 limit 2

/*markdown
# note that we cannot use "" for the strings
*/

select d.date, d.ticker, d.sumOC from 
    (select date, ticker, cast(open as int)+ cast(close as int) as sumOC
    from saffron.daily_price ) as d 
where d.sumOC between 260 and 300 and d.date <> '2018-04-25T00:00:00.000Z' and ticker is not NULL and ticker in ('A','F', 'FB')  limit 2


select date, ticker, open from saffron.daily_price where ticker like 'AB%' order by close limit 2

select date, ticker, open from saffron.daily_price where ticker like 'AB%' order by close limit 2