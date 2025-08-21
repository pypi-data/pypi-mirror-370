DECLARE
    LastModified DATE;
    RemovedCount NUMBER := 0;
    TotalCount NUMBER := 0;
BEGIN
    Let ListFiles RESULTSET:= (EXECUTE IMMEDIATE 'LS ' || {{ destination_stage }});
    LET C1 CURSOR FOR ListFiles;
    FOR files IN C1 DO
        TotalCount := TotalCount + 1;
        LastModified := TO_DATE(LEFT( files."last_modified", LENGTH(files."last_modified") - 4 ), 'DY, DD MON YYYY HH24:MI:SS' );
        IF (LastModified <= DATEADD( 'day', -1 * {{ days }}, current_timestamp())) THEN
            RemovedCount := RemovedCount + 1;
            EXECUTE IMMEDIATE 'RM @~/' || files."name";
        END IF;
    END FOR;
RETURN RemovedCount || ' of ' || TotalCount || ' files were deleted.';
END;
