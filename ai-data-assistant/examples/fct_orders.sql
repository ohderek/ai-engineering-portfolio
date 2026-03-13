-- fct_orders.sql
-- A realistic but intentionally imperfect model for the reviewer to flag.

select
    o.order_id,
    o.customer_id,
    o.created_at,
    o.status,
    sum(i.quantity * i.unit_price) as revenue,
    count(*) as line_items,
    c.country,
    c.plan_type
from orders o
join order_items i on o.order_id = i.order_id
join customers c on o.customer_id = c.customer_id
where o.status != 'cancelled'
group by 1, 2, 3, 4, 7, 8
