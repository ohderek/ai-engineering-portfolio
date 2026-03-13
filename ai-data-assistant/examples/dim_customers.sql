-- dim_customers.sql
-- Customer dimension model for doc generation demo.

with source as (
    select * from {{ source('app_db', 'customers') }}
),

cleaned as (
    select
        customer_id,
        lower(trim(email))          as email,
        coalesce(first_name, 'Unknown') as first_name,
        last_name,
        country_code,
        plan_type,
        created_at,
        updated_at,
        case
            when deleted_at is not null then true
            else false
        end                         as is_deleted
    from source
    where customer_id is not null
)

select * from cleaned
