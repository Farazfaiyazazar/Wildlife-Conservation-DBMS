-- ===============================================
-- PROJECT: Wildlife conservation monitoring system
-- COURSE: CMPE344 - Database management systems 2
-- DESCRIPTION: Database schema, Initial data, and PL/SQL
-- =================================================

-- 1. DATABASE TABLES (DDL)
--Roles for User Access Control
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL
);

--System Users (Authentication)
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL, 
    role_id INT REFERENCES roles(role_id)
);

--species Information
CREATE TABLE species (
    species_id SERIAL PRIMARY KEY,
    common_name VARCHAR(100),
    scientific_name VARCHAR(100),
    conservation_status VARCHAR(50)
);

--wildlife Habitats
CREATE TABLE habitats (
    habitat_id SERIAL PRIMARY KEY,
    area_name VARCHAR(100),
    location_coords VARCHAR(100),
    climate_type VARCHAR(50)
);

--Core Relational: Observations
CREATE TABLE observations (
    obs_id SERIAL PRIMARY KEY,
    species_id INT REFERENCES species(species_id),
    habitat_id INT REFERENCES habitats(habitat_id),
    observer_id INT REFERENCES users(user_id),
    observation_date DATE DEFAULT CURRENT_DATE,
    population_count INT CHECK (population_count >= 0)
);

--field Equipment
CREATE TABLE equipment (
    equip_id SERIAL PRIMARY KEY,
    habitat_id INT REFERENCES habitats(habitat_id),
    equip_type VARCHAR(50),
    status VARCHAR(20) DEFAULT 'Active'
);

-- 2. SAMPLE DATA (DML)
-- --------------------------------------------------------

INSERT INTO roles (role_name) VALUES ('Admin'), ('Researcher'), ('Technical Staff');

INSERT INTO users (username, password, role_id) VALUES ('admin_user', 'pass123', 1);

INSERT INTO species (common_name, scientific_name, conservation_status) 
VALUES ('African Elephant', 'Loxodonta africana', 'Vulnerable');

INSERT INTO habitats (area_name, location_coords, climate_type) 
VALUES ('Serengeti North', '2.33 S, 34.83 E', 'Savanna');

INSERT INTO observations (species_id, habitat_id, observer_id, population_count)
VALUES (1, 1, 1, 45);

-- 3. PL/SQL LOGIC (Triggers, Functions, & Procedures)

--Trigger Function: Prevent negative population counts
CREATE OR REPLACE FUNCTION check_count() 
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.population_count < 0 THEN
        RAISE EXCEPTION 'Population cannot be negative!';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_check_pop
BEFORE INSERT ON observations
FOR EACH ROW EXECUTE FUNCTION check_count();

--Procedure: Update equipment status easily
CREATE OR REPLACE PROCEDURE update_equip_status(eid INT, new_status VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE equipment SET status = new_status WHERE equip_id = eid;
END;
$$;

--Function: Get an alert
CREATE OR REPLACE FUNCTION get_status_warning(s_id INT) 
RETURNS TEXT AS $$
DECLARE
    stat TEXT;
BEGIN
    SELECT conservation_status INTO stat FROM species WHERE species_id = s_id;
    IF stat = 'Critically Endangered' THEN 
        RETURN 'URGENT ACTION REQUIRED';
    ELSE 
        RETURN 'Monitoring Ongoing';
    END IF;
END;
$$ LANGUAGE plpgsql;
