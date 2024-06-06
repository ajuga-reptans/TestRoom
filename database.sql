DO $$ DECLARE
    r RECORD;
BEGIN
    -- if the schema you operate on is not "public", you must change "public" to your schema name
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(r.tablename) || ' CASCADE';
    END LOOP;
END $$;

CREATE TABLE Users (
    id serial4 NOT NULL PRIMARY KEY,
    userName varchar UNIQUE,
    userPassword varchar
);

CREATE TABLE Categoty (
    id serial4 NOT NULL PRIMARY KEY,
    categotyName varchar
);

CREATE TABLE tests (
    id serial4 NOT NULL PRIMARY KEY,
    testName varchar,
    discribtion varchar,
    pictureLink varchar,
    likeCount integer,
    dislikeCount integer,
    fkUser serial4,
    fkCategory serial4,
    FOREIGN KEY (fkUser) REFERENCES Users (Id) ON DELETE CASCADE,
    FOREIGN KEY (fkCategory) REFERENCES Categoty (Id) ON DELETE CASCADE
);

CREATE TABLE testResultPack (
    id serial4 NOT NULL PRIMARY KEY,
    resId integer,
    resultName varchar,
    imgResult varchar,
    fkTest serial4,
    FOREIGN KEY (fkTest) REFERENCES tests (Id) ON DELETE CASCADE
);

CREATE TABLE questions (
    id serial4 NOT NULL PRIMARY KEY,
    questionName varchar,
    fkTest serial4,
    FOREIGN KEY (fkTest) REFERENCES tests (Id) ON DELETE CASCADE
);
CREATE TABLE answers (
    id serial4 NOT NULL PRIMARY KEY,
    anserName varchar,
    fkQuestion serial4,
    rusult integer,
    FOREIGN KEY (fkQuestion) REFERENCES questions (Id) ON DELETE CASCADE
);

INSERT INTO Users (userName, userPassword) VALUES ('root', '123'); 
INSERT INTO Categoty (categotyName) VALUES ('Все');
INSERT INTO Categoty (categotyName) VALUES ('кино и сериалы');
INSERT INTO Categoty (categotyName) VALUES ('компьютерные игры');
INSERT INTO Categoty (categotyName) VALUES ('любовь и отношения');
INSERT INTO Categoty (categotyName) VALUES ('интеллектуальные');
INSERT INTO Categoty (categotyName) VALUES ('психологические');
INSERT INTO Categoty (categotyName) VALUES ('для детей');
INSERT INTO Categoty (categotyName) VALUES ('для девушек');
INSERT INTO Categoty (categotyName) VALUES ('для парней');
INSERT INTO Categoty (categotyName) VALUES ('для старцев');