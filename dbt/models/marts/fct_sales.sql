select
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    oi.pizza_id,

    cast(o.ordered_at as date) as order_date,
    o.ordered_at,
    o.order_status,
    o.order_channel,
    o.delivery_prefecture,

    oi.quantity,
    oi.unit_price,
    oi.subtotal

from {{ ref('stg_order_items') }} oi

inner join {{ ref('stg_orders') }} o
    on oi.order_id = o.order_id
