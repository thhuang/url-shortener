CREATE DATABASE IF NOT EXISTS urlshortener;
USE urlshortener


DROP TABLE IF EXISTS urls;
CREATE TABLE urls
(
    urlid        int not null AUTO_INCREMENT,
    shorturl     varchar(16) not null,
    longurl      varchar(256) not null,
    PRIMARY KEY  (urlid),
    UNIQUE       (shorturl)
);


DROP TABLE IF EXISTS history;
CREATE TABLE history
(
    historyid    int not null AUTO_INCREMENT,
    urlid        int not null,
    created      datetime,
    ip           varchar(16),
    city         varchar(256),
    region       varchar(256),
    country      varchar(256),
    browser      varchar(256),
    os           varchar(256),
    device       varchar(256),
    PRIMARY KEY  (historyid),
    FOREIGN KEY  (urlid) REFERENCES urls(urlid)
);


CREATE USER 'urlshortener-read-only' IDENTIFIED BY 'abc123!!';
CREATE USER 'urlshortener-read-write' IDENTIFIED BY 'def456!!';

GRANT SELECT, SHOW VIEW ON urlshortener.* 
      TO 'urlshortener-read-only';
GRANT SELECT, SHOW VIEW, INSERT, UPDATE, DELETE, DROP, CREATE, ALTER ON urlshortener.* 
      TO 'urlshortener-read-write';
      
FLUSH PRIVILEGES;
