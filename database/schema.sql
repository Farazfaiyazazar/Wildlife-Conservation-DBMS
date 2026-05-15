-- Wildlife Registry Database Schema
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR NOT NULL
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR NOT NULL UNIQUE,
    password VARCHAR NOT NULL,
    role_id INTEGER REFERENCES roles(role_id)
);

CREATE TABLE species (
    species_id SERIAL PRIMARY KEY,
    common_name VARCHAR,
    scientific_name VARCHAR,
    conservation_status VARCHAR,
    population BIGINT
);

CREATE TABLE habitats (
    habitat_id SERIAL PRIMARY KEY,
    area_name VARCHAR,
    location_coords VARCHAR,
    climate_type VARCHAR
);

CREATE TABLE observations (
    obs_id SERIAL PRIMARY KEY,
    species_id INTEGER REFERENCES species(species_id),
    habitat_id INTEGER REFERENCES habitats(habitat_id),
    observer_id INTEGER REFERENCES users(user_id),
    population_count INTEGER,
    observation_date DATE
);

CREATE TABLE equipment (
    equip_id SERIAL PRIMARY KEY,
    equip_type VARCHAR,
    status VARCHAR,
    habitat_id INTEGER REFERENCES habitats(habitat_id)
);