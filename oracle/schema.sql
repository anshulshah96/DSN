DROP TABLE IF EXISTS challenge;
CREATE TABLE challenge (address varchar(255) NOT NULL UNIQUE,challenge varchar(255),size int);
-- INSERT INTO challenge VALUES ('abcdefabcedf','challenge1',001)