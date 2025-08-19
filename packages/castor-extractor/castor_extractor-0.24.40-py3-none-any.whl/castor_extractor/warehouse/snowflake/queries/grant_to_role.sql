SELECT
    created_on,
    modified_on,
    privilege,
    granted_on,
    name,
    table_catalog AS "database",
    table_schema AS "schema",
    granted_to,
    grantee_name,
    grant_option,
    granted_by,
    deleted_on
FROM snowflake.account_usage.grants_to_roles
