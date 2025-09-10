drop schema if exists "broiler_prediction" cascade;

create schema "broiler_prediction";

create table if not exists "broiler_prediction"."prediction_result" (
	id uuid,
	days integer not null,
	temperature numeric not null,
	humidity numeric not null,
	amonia numeric not null,
	food numeric not null,
	drink numeric not null,
	weight numeric not null,
	population integer not null,
	cage_area numeric not null,
	prediction numeric(1) not null,
	date_data_origin timestamp not null,
	date_created timestamp not null,
	
	primary key(id)
);

create table if not exists "broiler_prediction"."forecasting_result" (
	id uuid,
	temperature numeric not null,
	humidity numeric not null,
	amonia numeric not null,
	food numeric not null,
	drink numeric not null,
	weight numeric not null,
	population integer not null,
	cage_area numeric not null,
	class varchar(12) not null,
	prediction numeric(1) not null,
	date_data_origin timestamp not null,
	date_created timestamp not null,
	
	primary key(id)
);


-- new 
drop schema if exists "broiler_app" cascade;

create schema "broiler_app";

create table if not exists "broiler_app"."users" (
    id varchar primary key,
    username varchar not null,
	email varchar not null,
    created_at timestamp not null default now()
);

create table if not exists "broiler_app"."cages" (
    id varchar primary key,
    user_id varchar not null,
    initial_population integer,
	current_population integer,
    cage_area float,
    status varchar check (status in ('active', 'non-active')),
    date_activated timestamp,
	iot_id varchar,
    created_at timestamp not null default now(),
    constraint fk_cage_user foreign key (user_id) references "broiler_app"."users"(id)
);

create table if not exists "broiler_app"."daily_activity" (
    id varchar primary key,
    cage_id varchar not null,
    food float,
    drink float,
	weight float,
    death float,
    current_population integer,
    day integer not null,
    created_at timestamp not null default now(),
    constraint fk_activity_cage foreign key (cage_id) references "broiler_app"."cages"(id)
);

create table if not exists "broiler_app"."broiler_prediction" (
    id varchar primary key,
	iot_id varchar,
    cage_id varchar not null,
    humidity float,
    ammo float,
    temperature float,
    food float,
    drink float,
    weight float,
    current_population integer,
    cage_area float,
    hour float,
    session float,
    created_at timestamp not null default now(),
    constraint fk_prediction_cage foreign key (cage_id) references "broiler_app"."cages"(id)
);

create table if not exists "broiler_app"."log_notification" (
    id varchar primary key,
    user_id varchar not null,
    broiler_prediction_id varchar not null,
    message_code varchar not null,
    created_at timestamp not null default now(),
    constraint fk_log_user foreign key (user_id) references "broiler_app"."users"(id),
    constraint fk_log_prediction foreign key (broiler_prediction_id) references "broiler_app"."broiler_prediction"(id)
);

-- drop table if exists "broiler_app"."log_notification" cascade;
-- drop table if exists "broiler_app"."broiler_prediction" cascade;
-- drop table if exists "broiler_app"."daily_activity" cascade;
-- drop table if exists "broiler_app"."cages" cascade;
-- drop table if exists "broiler_app"."users" cascade;



