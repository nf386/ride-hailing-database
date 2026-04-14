SELECT DB_NAME() AS CurrentDatabase;


CREATE TABLE Users (
    user_id INT PRIMARY KEY IDENTITY(1,1),
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    phone_number VARCHAR(20) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT GETDATE()
);

CREATE TABLE Drivers (
    driver_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    licence_number VARCHAR(50) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);

CREATE TABLE Vehicles (
    vehicle_id INT PRIMARY KEY IDENTITY(1,1),
    driver_id INT NOT NULL UNIQUE,
    registration_number VARCHAR(20) NOT NULL UNIQUE,
    vehicle_model VARCHAR(100) NOT NULL,
    vehicle_colour VARCHAR(50) NOT NULL,
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id)
);

CREATE TABLE Trips (
    trip_id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    driver_id INT NOT NULL,
    vehicle_id INT NOT NULL,
    pickup_location VARCHAR(255) NOT NULL,
    dropoff_location VARCHAR(255) NOT NULL,
    trip_status VARCHAR(20) NOT NULL CHECK (trip_status IN ('booked', 'active', 'completed')),
    request_time DATETIME NOT NULL DEFAULT GETDATE(),
    start_time DATETIME NULL,
    end_time DATETIME NULL,
    fare_amount DECIMAL(10,2) NULL,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (driver_id) REFERENCES Drivers(driver_id),
    FOREIGN KEY (vehicle_id) REFERENCES Vehicles(vehicle_id)
);

CREATE TABLE Payments (
    payment_id INT PRIMARY KEY IDENTITY(1,1),
    trip_id INT NOT NULL UNIQUE,
    payment_amount DECIMAL(10,2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    payment_status VARCHAR(20) NOT NULL CHECK (payment_status IN ('pending', 'completed', 'failed')),
    payment_time DATETIME NOT NULL DEFAULT GETDATE(),
    FOREIGN KEY (trip_id) REFERENCES Trips(trip_id)
);

