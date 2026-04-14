SELECT DB_NAME() AS CurrentDatabase;

SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE';


INSERT INTO Users (full_name, email, phone_number)
VALUES
('Phil Rod', 'phil@email.com', '07111111111'),
('Alex Green', 'alex@email.com', '07222222222'),
('Morgan Reed', 'morgan@email.com', '07333333333');

SELECT * FROM Users;

INSERT INTO Drivers (user_id, licence_number)
VALUES
(2, 'LIC12345'),
(3, 'LIC67890');

SELECT * FROM Drivers;

INSERT INTO Vehicles (driver_id, registration_number, vehicle_model, vehicle_colour)
VALUES
(1, 'AB12CDE', 'Toyota Prius', 'White'),
(2, 'FG34HIJ', 'Honda Civic', 'Black');

SELECT * FROM Vehicles;

INSERT INTO Trips (
    user_id,
    driver_id,
    vehicle_id,
    pickup_location,
    dropoff_location,
    trip_status,
    start_time,
    end_time,
    fare_amount
)
VALUES
(1, 1, 1, 'Exeter St Davids', 'Exeter High Street', 'completed', GETDATE(), GETDATE(), 12.50),
(1, 2, 2, 'Exeter Quay', 'University of Exeter', 'active', GETDATE(), NULL, NULL);


SELECT * FROM Trips;

    INSERT INTO Payments (
        trip_id,
        payment_amount,
        payment_method,
        payment_status
    )
    VALUES
    (1, 12.50, 'card', 'completed');

SELECT * FROM Payments;

SELECT
    t.trip_id,
    u.full_name AS passenger_name,
    d.driver_id,
    v.registration_number,
    t.pickup_location,
    t.dropoff_location,
    t.trip_status,
    t.fare_amount
FROM Trips t
JOIN Users u ON t.user_id = u.user_id
JOIN Drivers d ON t.driver_id = d.driver_id
JOIN Vehicles v ON t.vehicle_id = v.vehicle_id;

SELECT * FROM Payments;
SELECT * FROM Drivers;



INSERT INTO Trips (
    user_id,
    driver_id,
    vehicle_id,
    pickup_location,
    dropoff_location,
    trip_status,
    start_time,
    end_time,
    fare_amount
)
VALUES
(1, 1, 1, 'Exeter St Davids', 'Exeter High Street', 'completed',
 DATEADD(MINUTE, -20, GETDATE()),
 DATEADD(MINUTE, -5, GETDATE()),
 12.50);


 INSERT INTO Trips (
    user_id,
    driver_id,
    vehicle_id,
    pickup_location,
    dropoff_location,
    trip_status,
    start_time,
    end_time,
    fare_amount
)
VALUES
(1, 2, 2, 'Exeter Quay', 'University of Exeter', 'active',
 DATEADD(MINUTE, -10, GETDATE()),
 NULL,
 NULL);


 INSERT INTO Trips (
    user_id,
    driver_id,
    vehicle_id,
    pickup_location,
    dropoff_location,
    trip_status,
    request_time,
    start_time,
    end_time,
    fare_amount
)
VALUES
(1, 1, 1, 'Exeter St Davids', 'Exeter High Street', 'completed',
 DATEADD(MINUTE, -25, GETDATE()),
 DATEADD(MINUTE, -20, GETDATE()),
 DATEADD(MINUTE, -5, GETDATE()),
 12.50);

 SELECT 
    trip_id,
    request_time,
    start_time,
    end_time,
    trip_status,
    fare_amount
FROM Trips;

SELECT *
FROM Trips
WHERE trip_id = 1;

SELECT * FROM Users;
SELECT * FROM Drivers;
SELECT * FROM Vehicles;
SELECT * FROM Trips;
SELECT * FROM Payments;

request_time DATETIME NOT NULL DEFAULT GETDATE()

SELECT 
    COLUMN_NAME, 
    DATA_TYPE, 
    IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'Trips';

SELECT 
    trip_id,
    request_time,
    start_time,
    end_time,
    trip_status,
    fare_amount
FROM Trips;

SELECT
    t.trip_id,
    u.full_name AS passenger,
    t.trip_status,
    t.request_time,
    t.start_time,
    t.end_time,
    t.fare_amount
FROM Trips t
JOIN Users u ON t.user_id = u.user_id;

UPDATE Trips
SET user_id = 2
WHERE trip_id = 3;

UPDATE Trips
SET user_id = 3
WHERE trip_id = 4;

UPDATE Trips
SET user_id = 4
WHERE trip_id = 5;

SELECT
    t.trip_id,
    u.full_name AS passenger,
    t.trip_status,
    t.request_time,
    t.start_time,
    t.end_time,
    t.fare_amount
FROM Trips t
JOIN Users u ON t.user_id = u.user_id;

SELECT
    t.trip_id,
    u.full_name AS passenger,
    d.driver_id,
    v.registration_number,
    t.pickup_location,
    t.dropoff_location,
    t.trip_status,
    t.fare_amount
FROM Trips t
JOIN Users u ON t.user_id = u.user_id
JOIN Drivers d ON t.driver_id = d.driver_id
JOIN Vehicles v ON t.vehicle_id = v.vehicle_id;



INSERT INTO dbo.Users (full_name, email, phone_number)
VALUES
('Sophie Turner', 'sophie.turner@email.com', '07411111111'),
('Daniel Carter', 'daniel.carter@email.com', '07522222222'),
('Priya Shah', 'priya.shah@email.com', '07633333333');

select *
from users

INSERT INTO dbo.Users (full_name, email, phone_number)
VALUES
('Jack Turner', 'jack.turner@email.com', '07411111223');

select *
from users

INSERT INTO dbo.Drivers (user_id, licence_number)
VALUES
(4, 'LIC54321'),
(5, 'LIC09876');


select *
from drivers

INSERT INTO dbo.Vehicles (driver_id, registration_number, vehicle_model, vehicle_colour)
VALUES
(5, 'XY21ZAB', 'Tesla Model 3', 'Blue'),
(6, 'LM55NOP', 'Ford Focus', 'Grey');

select *
from vehicles

select *
from trips

INSERT INTO dbo.Trips (
    user_id,
    driver_id,
    vehicle_id,
    pickup_location,
    dropoff_location,
    trip_status,
    request_time,
    start_time,
    end_time,
    fare_amount
)
VALUES
(1, 5, 6, 'Exeter Central Station', 'Exeter Business School', 'completed', GETDATE(), GETDATE(), GETDATE(), 15.75);

select *
from trips

INSERT INTO dbo.Payments (
    trip_id,
    payment_amount,
    payment_method,
    payment_status
)
VALUES
(6, 15.75, 'card', 'completed');

select *
from payments 