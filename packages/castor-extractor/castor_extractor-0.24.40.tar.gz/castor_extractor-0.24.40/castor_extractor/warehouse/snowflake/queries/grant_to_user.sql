SELECT
    created_on,
    deleted_on,
    role,
    granted_to,
    grantee_name,
    granted_by
FROM snowflake.account_usage.grants_to_users
