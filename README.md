# Pizza Data Platform

Windows 11 + Docker Desktop + WSL2 上で構築する、
個人学習用のデータマネジメント基盤です。

## Source System

Oracle AI Database 26ai Free

Schema: `PIZZA`

Tables:

- CUSTOMERS
- ORDERS
- ORDER_ITEMS
- PIZZAS
- PAYMENTS

## Architecture

Oracle AI Database 26ai Free
→ Airbyte (planned)
→ SeaweedFS
→ Parquet
→ DuckDB
→ dbt
→ Metabase

## Current Status

Phase 1 completed:

- SeaweedFS 4.48
- S3-compatible bucket: `pizza-lake`
- DuckDB 1.5.6
- Parquet write/read verified
- DuckDB SQL aggregation verified

## Next Step

Phase 2:

Oracle AI Database 26ai Free
→ Airbyte
→ SeaweedFS Raw Layer
