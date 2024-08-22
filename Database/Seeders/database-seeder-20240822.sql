CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

truncate "broiler_prediction"."prediction_result" cascade;

insert into "broiler_prediction"."prediction_result"(id, days, temperature, humidity, amonia, food, drink, weight, population, cage_area, prediction, date_data_origin, date_created) 
values (uuid_generate_v4(), 1, 25.5, 87.0, 2.46, 150, 346, 56, 8000, 336, 0, '2023-01-05 09:05:00', NOW());