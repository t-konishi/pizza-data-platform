select
    oi.order_item_id,
    oi.order_id,
    o.customer_id,
    oi.pizza_id,

-- ORDERED_ATはUTCで格納されている前提で、注文日をJSTに変換
cast(
    (o.ordered_at AT TIME ZONE 'UTC') AT TIME ZONE 'Asia/Tokyo'
    as date
) as order_date,
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
