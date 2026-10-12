with dates as (
    select
        cast(date_value as date) as date_day
    from generate_series(
        date '2020-01-01',
        date '2035-12-31',
        interval 1 day
    ) as t(date_value)
)

select
    cast(strftime(date_day, '%Y%m%d') as integer) as date_key,
    date_day,

    cast(extract(year from date_day) as integer) as year,
    cast(extract(quarter from date_day) as integer) as quarter,
    cast(extract(month from date_day) as integer) as month,
    cast(extract(day from date_day) as integer) as day_of_month,

    cast(extract(isodow from date_day) as integer) as day_of_week,

    strftime(date_day, '%Y-%m') as year_month,

    extract(isodow from date_day) in (6, 7) as is_weekend

from dates
