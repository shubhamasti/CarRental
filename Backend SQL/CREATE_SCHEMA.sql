-- DROP DATABASE car_Rental;

CREATE DATABASE car_Rental;

USE car_Rental;


CREATE TABLE CUSTOMER_DETAILS
( DL_NUMBER CHAR(8) NOT NULL,
  FNAME VARCHAR(25) NOT NULL,
  LNAME VARCHAR(25) NOT NULL,
  PHONE_NUMBER CHAR(10) NOT NULL,
  EMAIL_ID VARCHAR(30) NOT NULL,
  PWD VARCHAR(20) NOT NULL,
  STREET VARCHAR(30) NOT NULL,
  CITY VARCHAR(20) NOT NULL,
  STATE_NAME VARCHAR(20) NOT NULL,
  PINCODE CHAR(6) NOT NULL,
  CONSTRAINT CUSTOMERPK
  PRIMARY KEY (DL_NUMBER)
);

CREATE TABLE CAR_CATEGORY
( CATEGORY_NAME VARCHAR(25) NOT NULL,
  NO_OF_LUGGAGE INT NOT NULL,
  NO_OF_PERSON INT NOT NULL,
  COST_PER_DAY FLOAT(5,2) NOT NULL,
  LATE_FEE_PER_DAY FLOAT(5,2) NOT NULL,
  CONSTRAINT CARCATEGORYPK
  PRIMARY KEY (CATEGORY_NAME)
);

CREATE TABLE LOCATION_DETAILS
( LOCATION_ID CHAR(4) NOT NULL,
  LOCATION_NAME VARCHAR(50) NOT NULL,
  STREET VARCHAR(30) NOT NULL,
  CITY VARCHAR(20) NOT NULL,
  STATE_NAME VARCHAR(20) NOT NULL,
  PINCODE CHAR(5) NOT NULL,
  CONSTRAINT LOCATIONPK
  PRIMARY KEY (LOCATION_ID)
);

CREATE TABLE CAR
( REGISTRATION_NUMBER CHAR(7) NOT NULL,
  MODEL_NAME VARCHAR(25) NOT NULL,
  MAKE VARCHAR(25) NOT NULL,
  MODEL_YEAR INT(4) NOT NULL,
  MILEAGE INT NOT NULL,
  CATEGORY_NAME VARCHAR(25) NOT NULL,
  LOCATION_ID CHAR(4) NOT NULL,
  AVAILABILITY_FLAG ENUM("Y", "N") NOT NULL,
  CONSTRAINT CARPK
  PRIMARY KEY (REGISTRATION_NUMBER),
  CONSTRAINT CARFK1
  FOREIGN KEY (CATEGORY_NAME) REFERENCES CAR_CATEGORY(CATEGORY_NAME),
  CONSTRAINT CARFK2
  FOREIGN KEY (LOCATION_ID) REFERENCES LOCATION_DETAILS(LOCATION_ID)
);


CREATE TABLE BOOKING_DETAILS
( BOOKING_ID CHAR(5) NOT NULL,
  FROM_DT_TIME DATE NOT NULL,
  RET_DT_TIME DATE NOT NULL,
  AMOUNT FLOAT(10,2) NOT NULL,
  -- R: returned, C: currently in use
  BOOKING_STATUS ENUM("R", "C", "B") NOT NULL,
  PICKUP_LOC  CHAR(4) NOT NULL,
  DROP_LOC CHAR(4) NOT NULL,
  REGISTRATION_NUMBER CHAR(7) NOT NULL,
  DL_NUMBER CHAR(8) NOT NULL,
  ACT_RET_DT_TIME DATE,
  LATE_FEE FLOAT(10,2) DEFAULT 0,
  TAX_AMOUNT FLOAT(10,2) DEFAULT 0,
  CONSTRAINT BOOKINGPK
  PRIMARY KEY (BOOKING_ID),
  CONSTRAINT BOOKINGFK1
  FOREIGN KEY (PICKUP_LOC) REFERENCES LOCATION_DETAILS(LOCATION_ID),
  CONSTRAINT BOOKINGFK2
  FOREIGN KEY (DROP_LOC) REFERENCES LOCATION_DETAILS(LOCATION_ID),
  CONSTRAINT BOOKINGFK3
  FOREIGN KEY (REGISTRATION_NUMBER) REFERENCES CAR(REGISTRATION_NUMBER),
  CONSTRAINT BOOKINGFK4
  FOREIGN KEY (DL_NUMBER) REFERENCES CUSTOMER_DETAILS(DL_NUMBER)
);

CREATE TABLE BILLING_DETAILS
( BILL_ID CHAR(6) NOT NULL,
  BILL_DATE DATE NOT NULL,
  -- P: paid, D: due
  BILL_STATUS ENUM("P", "D") NOT NULL,
  TOTAL_AMOUNT FLOAT(10,2) NOT NULL,
  TAX_AMOUNT FLOAT(10,2) NOT NULL,
  BOOKING_ID CHAR(5) NOT NULL,
  LATE_FEE FLOAT(10,2) NOT NULL,
  CONSTRAINT BILLINGPK
  PRIMARY KEY (BILL_ID),
  CONSTRAINT BILLINGFK1
  FOREIGN KEY (BOOKING_ID) REFERENCES BOOKING_DETAILS(BOOKING_ID)
);


CREATE OR REPLACE VIEW TABLE1 AS 
SELECT LC.LID AS LOCATIONID, LC.CNAME AS CATNAME ,COUNT(C.REGISTRATION_NUMBER) AS NOOFCARS 
FROM (SELECT L.LOCATION_ID AS LID, CC.CATEGORY_NAME AS CNAME FROM 
CAR_CATEGORY CC CROSS JOIN LOCATION_DETAILS L) LC LEFT OUTER JOIN CAR C 
ON LC.CNAME = C.CATEGORY_NAME AND LC.LID = C.LOCATION_ID GROUP BY LC.LID, 
LC.CNAME ORDER BY LC.LID;

CREATE OR REPLACE VIEW TABLE2 AS
SELECT BC.PLOC AS PICKLOC, BC.CNAME AS CNAMES, SUM(BL.TOTAL_AMOUNT) AS AMOUNT FROM
(SELECT B.PICKUP_LOC AS PLOC, C1.CATEGORY_NAME AS CNAME, B.BOOKING_ID AS BID
FROM BOOKING_DETAILS B INNER JOIN CAR C1 ON B.REGISTRATION_NUMBER = C1.REGISTRATION_NUMBER) BC
INNER JOIN BILLING_DETAILS BL ON BC.BID = BL.BOOKING_ID
WHERE DATEDIFF(CURDATE(), STR_TO_DATE(BL.BILL_DATE, '%d-%m-%Y')) <= 30
GROUP BY BC.PLOC, BC.CNAME ORDER BY BC.PLOC;