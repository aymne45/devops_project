CREATE KEYSPACE ent_ests
WITH replication = {
   'class': 'NetworkTopologyStrategy',
   'datacenter1': 1
};

USE ent_ests;

CREATE TABLE utilisateurs_par_email (
    email TEXT PRIMARY KEY,
    id_user UUID,
    username TEXT,
    password_hash TEXT,
    role TEXT,
    is_active BOOLEAN,
    created_at TIMESTAMP
);


CREATE TABLE utilisateurs_par_id (
    id_user UUID PRIMARY KEY,
    email TEXT,
    username TEXT,
    nom TEXT,
    prenom TEXT,
    role TEXT,
    created_at TIMESTAMP,
    is_active BOOLEAN
);


CREATE TABLE refresh_tokens (
    id_user UUID,
    refresh_token TEXT,
    expires_at TIMESTAMP,
    PRIMARY KEY (id_user, refresh_token)
);


CREATE TABLE departements (
    id_dept UUID PRIMARY KEY,
    nom_dept TEXT,
    description TEXT
);


CREATE TABLE filieres (
    id_filiere UUID PRIMARY KEY,
    nom_filiere TEXT,
    id_dept UUID,
    nom_dept TEXT
);


CREATE TABLE etudiants_par_id (
    id_user UUID PRIMARY KEY,
    num_apogee TEXT,
    id_filiere UUID,
    nom_filiere TEXT,
    niveau TEXT
);


CREATE TABLE etudiants_par_filiere (
    id_filiere UUID,
    id_user UUID,
    nom TEXT,
    prenom TEXT,
    num_apogee TEXT,
    niveau TEXT,
    PRIMARY KEY (id_filiere, id_user)
);


CREATE TABLE enseignants_par_id (
    id_user UUID PRIMARY KEY,
    specialite TEXT,
    id_dept UUID,
    nom_dept TEXT
);


CREATE TABLE enseignants_par_departement (
    id_dept UUID,
    id_user UUID,
    nom TEXT,
    prenom TEXT,
    specialite TEXT,
    PRIMARY KEY (id_dept, id_user)
);


CREATE TABLE cours_par_filiere (
    id_filiere UUID,
    date_upload TIMESTAMP,
    id_cours UUID,
    titre TEXT,
    description TEXT,
    enseignant_id UUID,
    enseignant_nom TEXT,
    url_minio TEXT,
    bucket_minio TEXT,
    nom_fichier TEXT,
    type_fichier TEXT,
    taille_fichier TEXT,
    PRIMARY KEY (id_filiere, date_upload)
) WITH CLUSTERING ORDER BY (date_upload DESC);


CREATE TABLE cours_par_enseignant (
    id_enseignant UUID,
    date_upload TIMESTAMP,
    id_cours UUID,
    titre TEXT,
    id_filiere UUID,
    nom_filiere TEXT,
    url_minio TEXT,
    PRIMARY KEY (id_enseignant, date_upload)
) WITH CLUSTERING ORDER BY (date_upload DESC);


CREATE TABLE cours_par_id (
    id_cours UUID PRIMARY KEY,
    titre TEXT,
    description TEXT,
    id_filiere UUID,
    nom_filiere TEXT,
    enseignant_id UUID,
    enseignant_nom TEXT,
    date_upload TIMESTAMP,
    url_minio TEXT,
    bucket_minio TEXT,
    nom_fichier TEXT,
    type_fichier TEXT,
    taille_fichier TEXT
);