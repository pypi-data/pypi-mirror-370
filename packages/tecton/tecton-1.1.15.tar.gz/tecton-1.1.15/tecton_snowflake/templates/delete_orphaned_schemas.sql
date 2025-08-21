DECLARE
    EmptyCount NUMBER := 0;
    TotalCount NUMBER := 0;
    ListSchemas RESULTSET;
    IsEmpty RESULTSET;
BEGIN
    ListSchemas := (EXECUTE IMMEDIATE 'SHOW SCHEMAS IN DATBASE {{ snowflake_database }}');
    LET C1 CURSOR FOR ListSchemas;
FOR availableSchema IN C1 DO
        Let availableSchemaName VARCHAR := availableSchema."name";
        TotalCount := TotalCount + 1;
        IsEmpty := (EXECUTE IMMEDIATE 'SELECT ''' || availableSchemaName || ''' AS schema_name,
           CASE WHEN EXISTS (
              SELECT 1 FROM {{ snowflake_database }}.INFORMATION_SCHEMA.TABLES WHERE TABLE_SCHEMA ILIKE ''' || availableSchemaName || '''
              UNION ALL
              SELECT 1 FROM {{ snowflake_database }}.INFORMATION_SCHEMA.VIEWS WHERE TABLE_SCHEMA ILIKE ''' || availableSchemaName || '''
             ) THEN 0
               ELSE 1
        END is_empty');
        LET C2 CURSOR FOR IsEmpty;
        FOR maybeEmptySchema IN C2 DO
            If (maybeEmptySchema."IS_EMPTY" = 1) then
                EmptyCount := EmptyCount + 1;
                EXECUTE IMMEDIATE 'DROP SCHEMA IF EXISTS ' || availableSchemaName;
            END IF;
        END FOR;
END FOR;
RETURN EmptyCount || ' of ' || TotalCount || ' schemas are empty.';
END;
