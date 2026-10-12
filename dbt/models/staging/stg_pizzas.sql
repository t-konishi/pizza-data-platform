select
    cast(PIZZA_ID as bigint)             as pizza_id,
    PIZZA_NAME                           as pizza_name,
    DESCRIPTION                          as description,
    cast(PRICE as decimal(12, 2))        as price,
    CATEGORY                             as category,
    cast(ACTIVE as integer) = 1          as is_active,
    try_cast(CREATED_AT as timestamp)    as created_at,
    try_cast(UPDATED_AT as timestamp)    as updated_at
from read_parquet(
    's3://pizza-lake/raw/oracle/PIZZA/PIZZAS/*.parquet',
    union_by_name = true
)
