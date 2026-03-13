"""
Prompt Engineering — the heart of Step 2 on the AI Engineer Roadmap.

This module demonstrates three key techniques:
1. System prompts     — give the model a persona and constraints
2. Few-shot examples  — show the model what "good" looks like
3. Structured outputs — force responses into a predictable schema
"""

# ── 1. System Prompts ────────────────────────────────────────────────────────

SQL_REVIEWER_SYSTEM = """You are a senior data engineer specializing in SQL best practices,
query performance, and analytics engineering (dbt). Your reviews are direct, specific,
and actionable.

When reviewing SQL you always check for:
- Performance: missing filters on large tables, unnecessary cross joins, fan-out issues
- Correctness: grain ambiguity, incorrect aggregations, NULLs in joins
- Style: CTE naming, column aliasing, readability
- dbt conventions: ref() usage, source() macros, test coverage gaps

Format your feedback as numbered issues with severity [HIGH / MEDIUM / LOW]
followed by a concrete suggested fix."""

DOC_GENERATOR_SYSTEM = """You are a documentation specialist for dbt (data build tool) projects.
Your job is to generate accurate, concise schema.yml documentation from SQL model definitions.

Rules:
- Column descriptions must be one clear sentence, no fluff
- Infer data types from SQL expressions and aliases
- Flag columns that should have dbt tests (primary keys, foreign keys, not-null fields)
- Output valid YAML only — no markdown fences, no extra commentary"""

CHAT_SYSTEM = """You are a helpful data engineering assistant with deep expertise in:
SQL, dbt Core, Snowflake, Apache Airflow, Prefect, and analytics engineering.

Keep answers concise and practical. When showing code, use the user's stack (Python/SQL/dbt).
If a question is ambiguous, ask one clarifying question before answering."""


# ── 2. Few-Shot Examples ─────────────────────────────────────────────────────

FEW_SHOT_DOC_EXAMPLES = [
    {
        "role": "user",
        "content": """Generate schema.yml documentation for this model:

```sql
select
    order_id,
    customer_id,
    order_date,
    sum(line_total) as order_total,
    count(line_item_id) as item_count
from {{ ref('stg_orders') }}
join {{ ref('stg_order_items') }} using (order_id)
group by 1, 2, 3
```
Model name: fct_orders""",
    },
    {
        "role": "assistant",
        "content": """version: 2

models:
  - name: fct_orders
    description: One row per order with aggregated line item totals.
    columns:
      - name: order_id
        description: Unique identifier for each order.
        tests:
          - unique
          - not_null
      - name: customer_id
        description: Foreign key to dim_customers.
        tests:
          - not_null
          - relationships:
              to: ref('dim_customers')
              field: customer_id
      - name: order_date
        description: Date the order was placed.
        tests:
          - not_null
      - name: order_total
        description: Sum of all line item totals for the order.
      - name: item_count
        description: Number of distinct line items on the order.""",
    },
]
