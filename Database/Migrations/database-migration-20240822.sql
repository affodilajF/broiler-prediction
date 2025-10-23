drop schema if exists "broiler_app" cascade;
create schema "broiler_app";

create table if not exists "broiler_app"."users" (
    firebase_id varchar primary key,
    name varchar not null,
    province varchar not null,
    city varchar not null,
    phone varchar not null,
    email varchar not null,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS "broiler_app"."devices" (
    device_id VARCHAR PRIMARY KEY,
    status VARCHAR,
    CONSTRAINT chk_device_status CHECK (status IN ('online', 'offline')),
    last_updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

CREATE TABLE IF NOT EXISTS "broiler_app"."device_data" (
    id SERIAL PRIMARY KEY,
    device_id VARCHAR NOT NULL,
    temperature FLOAT, 
    humidity FLOAT, 
    ammonia FLOAT,
    -- timestamp INTEGER,
    -- timestamp TIMESTAMPTZ
    zone_offset INTEGER,
    timestamp TIMESTAMP WITH TIME ZONE,
    CONSTRAINT fk_data_devices FOREIGN KEY (device_id) REFERENCES "broiler_app"."devices"(device_id)
);

create table if not exists "broiler_app"."cages" (
    id VARCHAR PRIMARY KEY,
    firebase_id VARCHAR NOT NULL,
    cage_name VARCHAR NOT NULL,
    cage_area FLOAT,
    device_id VARCHAR NOT NULL,
    initial_population INTEGER,
    current_population INTEGER,
    status VARCHAR,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),

    CONSTRAINT fk_cages_users FOREIGN KEY (firebase_id) REFERENCES "broiler_app"."users"(firebase_id),
    CONSTRAINT fk_cages_devices FOREIGN KEY (device_id) REFERENCES "broiler_app"."devices"(device_id),
    CONSTRAINT chk_cages_status CHECK (status IN ('active', 'non-active'))
);

create table if not exists "broiler_app"."cage_activation_detail" (
    cage_id VARCHAR NOT NULL PRIMARY KEY,   
    date_activated TIMESTAMP WITH TIME ZONE, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now(),
    CONSTRAINT fk_activation_cage FOREIGN KEY (cage_id) REFERENCES "broiler_app"."cages"(id)
);

create table if not exists "broiler_app"."daily_activity" (
    id varchar primary key,
    cage_id varchar not null,
    date timestamp,
    food float,
    drink float,
	weight float,
    death float,
    notes text,
    created_at timestamp not null default now(),
    constraint fk_activity_cage foreign key (cage_id) references "broiler_app"."cages"(id)
);

create table if not exists "broiler_app"."broiler_predictions" (
    id varchar primary key,
    cage_id varchar not null,
    prediction_status VARCHAR,
    CONSTRAINT chk_prediction_status CHECK (prediction_status IN ('success', 'failed')),
    error INTEGER, 
    created_at timestamp not null default now(),
    constraint fk_cage foreign key (cage_id) references "broiler_app"."cages"(id)
);

CREATE TABLE IF NOT EXISTS "broiler_app"."broiler_prediction_detail" (
    id VARCHAR PRIMARY KEY,
    device_id VARCHAR,
    device_timestamp TIMESTAMP WITH TIME ZONE,
    device_zone_offset INTEGER,
    broiler_prediction_id VARCHAR NOT NULL,
    prediction_result VARCHAR,
    CONSTRAINT chk_prediction_result CHECK (prediction_result IN ('normal', 'abnormal', 'cannot predict')),
    humidity FLOAT,
    ammo FLOAT,
    temperature FLOAT,
    food FLOAT,
    drink FLOAT,
    weight FLOAT,
    current_population INTEGER,
    cage_area FLOAT,
    session FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_broiler_prediction_detail FOREIGN KEY (broiler_prediction_id) REFERENCES "broiler_app"."broiler_predictions"(id)
);

CREATE TABLE IF NOT EXISTS "broiler_app"."log_notifications" (
    id VARCHAR PRIMARY KEY,
    cage_id VARCHAR NOT NULL,
    cage_name VARCHAR,
    firebase_id VARCHAR NOT NULL,
    broiler_prediction_id VARCHAR NOT NULL,
    read_status BOOLEAN DEFAULT FALSE,
    prediction_result VARCHAR,
    CONSTRAINT chk_prediction_result CHECK (prediction_result IN ('abnormal', 'cannot predict')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    CONSTRAINT fk_cage FOREIGN KEY (cage_id) REFERENCES "broiler_app"."cages"(id),
    CONSTRAINT fk_notification_user FOREIGN KEY (firebase_id) REFERENCES "broiler_app"."users"(firebase_id),
    CONSTRAINT fk_notification_prediction FOREIGN KEY (broiler_prediction_id) REFERENCES "broiler_app"."broiler_predictions"(id)
);


