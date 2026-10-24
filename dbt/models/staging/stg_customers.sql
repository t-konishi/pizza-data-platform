select
    cast(CUSTOMER_ID as bigint)          as customer_id,
    CUSTOMER_NAME                       as customer_name,
    EMAIL                               as email,
    PHONE                               as phone,
    cast(ACTIVE as integer) = 1         as is_active,
    try_cast(REGISTERED_AT as timestamp) as registered_at,
    try_cast(CREATED_AT as timestamp)    as created_at,
    try_cast(UPDATED_AT as timestamp)    as updated_at
from read_parquet(
    's3://pizza-lake/raw/oracle/PIZZA/CUSTOMERS/*.parquet',
    union_by_name = true
)
where _airbyte_generation_id = {{ var('airbyte_generation_id') }}
