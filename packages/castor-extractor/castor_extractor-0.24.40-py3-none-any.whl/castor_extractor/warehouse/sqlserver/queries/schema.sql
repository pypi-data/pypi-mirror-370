/*
Fetch database information

Collation is a set of rules that defines how text data is stored and compared, and it can differ between databases.
The "COLLATE DATABASE_DEFAULT" is to ensure that text is compared with the same collation.
 */
WITH ids AS (
    SELECT DISTINCT
        table_catalog,
        table_schema
    FROM {database}.information_schema.tables
)

SELECT
    d.database_id,
    database_name = i.table_catalog,
    schema_name = s.name,
    schema_id = CAST(d.database_id AS VARCHAR(10)) + '_' + CAST(s.schema_id AS VARCHAR(10)),
    schema_owner = u.name,
    schema_owner_id = u.uid
FROM {database}.sys.schemas AS s
INNER JOIN ids AS i
    ON s.name = i.table_schema
LEFT JOIN {database}.sys.sysusers AS u
    ON s.principal_id = u.uid
LEFT JOIN {database}.sys.databases AS d
    ON i.table_catalog COLLATE DATABASE_DEFAULT = d.name COLLATE DATABASE_DEFAULT
