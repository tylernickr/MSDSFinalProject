DROP database if exists github;

CREATE database github;

USE github;


CREATE TABLE github_user
(
	username	varchar(80)		PRIMARY KEY,
    email		varchar(120) 	NOT NULL
);


CREATE TABLE project
(
	id			varchar(255)	PRIMARY KEY
);


CREATE table commit
(
	hash			char(40)		PRIMARY KEY,
    projectID		varchar(255)	NOT NULL,
    author			varchar(80)		NOT NULL,
    authorTime		datetime		NOT NULL,
    committer		varchar(80)		NOT NULL,
    commitTime		datetime		NOT NULL,
    subject			varchar(2048)	NOT NULL,
    FOREIGN KEY project_key(projectID) REFERENCES project(id),
    FOREIGN KEY author_key(author) REFERENCES github_user(username),
    FOREIGN KEY committer_key(committer) REFERENCES github_user(username)
)
ENGINE = MYISAM;


CREATE table file_modification
(
	hash	char(40)	 NOT NULL,
    file	varchar(560) NOT NULL,
    added   int			 NOT NULL,
    deleted int			 NOT NULL
)
ENGINE = MYISAM;


CREATE TABLE authorship_score
(
    projectID       varchar(255) NOT NULL,
    authorshipScore numeric(16,4) NOT NULL,
    FOREIGN KEY project_key(projectID) REFERENCES project(id)
)
ENGINE = MYISAM;

USE github;

DROP TABLE if exists bug_labels;

CREATE TABLE bug_labels
(
    hash    char(40)    PRIMARY KEY,
    isBug   char(1)     NOT NULL,
    bugCategory char(1) NULL
)
ENGINE = MYISAM;

CREATE TABLE commit_bug_labels
(
	hash	char(40)	PRIMARY KEY,
    isBug	char(1)		NOT NULL
)
ENGINE = MYISAM;
