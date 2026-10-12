select
    pizza_id,
    pizza_name,
    description,
    price as current_price,
    category,
    is_active,
    created_at,
    updated_at
from {{ ref('stg_pizzas') }}
