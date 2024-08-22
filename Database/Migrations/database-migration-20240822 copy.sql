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