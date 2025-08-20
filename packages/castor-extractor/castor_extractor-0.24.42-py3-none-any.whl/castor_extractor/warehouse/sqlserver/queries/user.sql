SELECT
    user_name = u.name,
    user_id = u.principal_id
FROM sys.database_principals AS u
