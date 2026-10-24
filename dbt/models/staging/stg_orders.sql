select
    cast(ORDER_ID as bigint)             as order_id,
    cast(CUSTOMER_ID as bigint)          as customer_id,
    ORDER_STATUS                         as order_status,
    cast(ORDER_TOTAL as decimal(12, 2))  as order_total,
    ORDER_CHANNEL                        as order_channel,
    DELIVERY_POSTAL_CODE                 as delivery_postal_code,
    DELIVERY_PREFECTURE                  as delivery_prefecture,
    DELIVERY_CITY                        as delivery_city,
    DELIVERY_ADDRESS1                    as delivery_address1,
    DELIVERY_ADDRESS2                    as delivery_address2,
    try_cast(ORDERED_AT as timestamp)    as ordered_at,
    try_cast(CREATED_AT as timestamp)    as created_at,
    try_cast(UPDATED_AT as timestamp)    as updated_at
from read_parquet(
    's3://pizza-lake/raw/oracle/PIZZA/ORDERS/*.parquet',
    union_by_name = true
)
where _airbyte_generation_id = {{ var('airbyte_generation_id') }}
