DROP TRIGGER IF EXISTS GENERATE_BILLING;
DELIMITER //

CREATE TRIGGER GENERATE_BILLING
AFTER UPDATE ON BOOKING_DETAILS
FOR EACH ROW
BEGIN
    -- DECLARE next_id VARCHAR(255);
    DECLARE newBillId VARCHAR(255); -- Adjust the size as per your column definition
    DECLARE totalLateFee DECIMAL(10,2);
    DECLARE totalTax DECIMAL(10,2);
    DECLARE totalAmount DECIMAL(10,2);

    -- SELECT CONCAT('BL', LPAD(IFNULL(CONVERT(SUBSTRING(MAX(BILL_ID), 3), UNSIGNED INTEGER), 0) + 1, 3, '0')) INTO newBillId
    -- FROM BILLING_DETAILS;

    -- Calculate the next lexicographically available ID for table2
    SELECT CONCAT('BL', LPAD(CAST(SUBSTRING(MAX(BILL_ID), 3) + 1 AS UNSIGNED), 3, '0'))
    INTO newBillId
    FROM BILLING_DETAILS;

    SET totalAmount = NEW.AMOUNT + NEW.LATE_FEE + NEW.TAX_AMOUNT;

    -- If no rows are present in table2, set the initial value
    IF newBillId IS NULL THEN
        SET newBillId = 'BL001';
    END IF;

    -- Insert a new row into table2 with the calculated ID
    -- INSERT INTO table2 (id, other_column)
    -- VALUES (next_id, NEW.other_column); -- Adjust 'other_column' based on your schema

    INSERT INTO BILLING_DETAILS (BILL_ID, BILL_DATE, BILL_STATUS, TOTAL_AMOUNT, TAX_AMOUNT, BOOKING_ID, LATE_FEE)
    VALUES (newBillId, CURDATE(), 'D', totalAmount, NEW.TAX_AMOUNT, NEW.BOOKING_ID, NEW.LATE_FEE);

END;
//
DELIMITER ;

