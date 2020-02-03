CREATE TABLE contents (
id  integer NOT NULL PRIMARY KEY auto_increment,
fiction_id  integer NOT NULL,
chapter_id  dec(20,2) NOT NULL,
content  text NOT NULL);

CREATE TABLE chapters (
id  integer NOT NULL PRIMARY KEY auto_increment,
fiction_id  integer NOT NULL,
chapter_id  dec(20,2) NOT NULL,
name  varchar(200) NOT NULL,
url  varchar(200) NOT NULL);

CREATE TABLE fictions (
id  integer NOT NULL PRIMARY KEY auto_increment,
name  varchar(200) NOT NULL,
url  varchar(200) NOT NULL,
fiction_id  integer NOT NULL);
