with daily_sales as (
    select
        order_date,
        count(distinct order_id) as order_count,
        sum(quantity) as total_quantity,
        sum(subtotal) as total_amount
    from {{ ref('fct_sales') }}
    where order_date is not null
    group by order_date
),

date_bounds as (
    select
        min(order_date) as min_date,
        max(order_date) as max_date
    from {{ ref('fct_sales') }}
)

select
    d.date_day,
    d.year,
    d.month,
    d.day_of_week,
    d.is_weekend,

    coalesce(s.order_count, 0) as order_count,
    coalesce(s.total_quantity, 0) as total_quantity,
    coalesce(s.total_amount, 0) as total_amount

from {{ ref('dim_date') }} d

cross join date_bounds b

left join daily_sales s
    on d.date_day = s.order_date

where d.date_day between
    b.min_date - interval 3 day
    and b.max_date + interval 3 day

order by d.date_day
