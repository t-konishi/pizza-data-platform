select
    cast(PAYMENT_ID as bigint)           as payment_id,
    cast(ORDER_ID as bigint)             as order_id,
    PAYMENT_METHOD                       as payment_method,
    PAYMENT_STATUS                       as payment_status,
    PROVIDER_TRANSACTION_ID              as provider_transaction_id,
    cast(AMOUNT as decimal(12, 2))       as amount,
    try_cast(PAID_AT as timestamp)       as paid_at,
    try_cast(CREATED_AT as timestamp)    as created_at,
    try_cast(UPDATED_AT as timestamp)    as updated_at
from read_parquet(
    's3://pizza-lake/raw/oracle/PIZZA/PAYMENTS/*.parquet',
    union_by_name = true
)
