select
    customer_id,
    customer_name,
    email,
    phone,
    is_active,
    registered_at,
    created_at,
    updated_at
from {{ ref('stg_customers') }}
