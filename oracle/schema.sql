DROP TABLE IF EXISTS challenge;
DROP TABLE IF EXISTS seed;
CREATE TABLE challenge (address varchar(255),challenge varchar(255),solution int,size int,url varchar(255));
CREATE TABLE seed (address varchar(255),seed varchar(255));
