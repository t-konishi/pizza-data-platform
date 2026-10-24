select
    cast(ORDER_ITEM_ID as bigint)        as order_item_id,
    cast(ORDER_ID as bigint)             as order_id,
    cast(PIZZA_ID as bigint)             as pizza_id,
    PIZZA_NAME                           as pizza_name,
    cast(QUANTITY as integer)            as quantity,
    cast(UNIT_PRICE as decimal(12, 2))   as unit_price,
    cast(SUBTOTAL as decimal(12, 2))     as subtotal,
    try_cast(CREATED_AT as timestamp)    as created_at,
    try_cast(UPDATED_AT as timestamp)    as updated_at
from read_parquet(
    's3://pizza-lake/raw/oracle/PIZZA/ORDER_ITEMS/*.parquet',
    union_by_name = true
)
where _airbyte_generation_id = {{ var('airbyte_generation_id') }}
