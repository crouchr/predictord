USE metminidb;
CREATE TABLE forecasts
(
id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
ts_local DATETIME NOT NULL,
ts_utc DATETIME NOT NULL,
julian INT NOT NULL,
location VARCHAR(64) NOT NULL,
pressure INT NOT NULL,
ptrend VARCHAR(10) NOT NULL,
wind_deg INT NOT NULL,
wind_strength INT NOT NULL,
slope FLOAT NOT NULL,
source VARCHAR(32) NOT NULL,
forecast_hughes38 VARCHAR(128) NOT NULL,
forecast_zambretti VARCHAR(128) NOT NULL,
container_version VARCHAR(8) NOT NULL
);
