DROP TABLE IF EXISTS Request;
DROP TABLE IF EXISTS Task;
DROP TABLE IF EXISTS Performer;
DROP TABLE IF EXISTS Area;
DROP TABLE IF EXISTS Customer;
DROP TABLE IF EXISTS Otkliki;
DROP TABLE IF EXISTS View_vacancies;
DROP TABLE IF EXISTS View_summary;
DROP TABLE IF EXISTS Vacancy;
DROP TABLE IF EXISTS Summary;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS Post_industry;
DROP TABLE IF EXISTS Post;
DROP TABLE IF EXISTS Industry;
DROP TABLE IF EXISTS Company;
DROP TABLE IF EXISTS Person;


CREATE TABLE Person(
    userid SERIAL PRIMARY KEY,
    login VARCHAR(15) NOT NULL UNIQUE,
    password TEXT NOT NULL,
    status TEXT  NOT NULL,
    email TEXT NOT NUlL UNIQUE,
    phone TEXT NOT NULL UNIQUE
);    

CREATE TABLE Company(
    userid INTEGER PRIMARY KEY REFERENCES Person(userid) ON DELETE CASCADE,
    INN VARCHAR(12) NOT NULL UNIQUE,
    Name_firm VARCHAR(255) NOT NULL,
    Balance NUMERIC CHECK(Balance >= 0) NOT NULL ,
    Employer_name VARCHAR(255) NOT NULL,
    Employer_surname VARCHAR(255) NOT NULL  
);

CREATE TABLE Industry(
    Name_industry VARCHAR(70) PRIMARY KEY NOT NULL
);


CREATE TABLE Post(
    Name_post VARCHAR(255) PRIMARY KEY NOT NULL   
);

CREATE TABLE Post_industry(
    industry_name TEXT NOT NULL,
    post_name TEXT NOT NULL,
    FOREIGN KEY(industry_name) REFERENCES Industry(Name_industry) ON UPDATE CASCADE,
    FOREIGN KEY(post_name) REFERENCES Post(Name_post) ON UPDATE CASCADE
);

CREATE TABLE Employee(
    userid INTEGER PRIMARY KEY REFERENCES Person(userid) ON DELETE CASCADE,
    FIO VARCHAR(255) NOT NULL,
    Sex VARCHAR(7) NOT NULL,
    Age VARCHAR(3) NOT NULL
);

CREATE TABLE Summary(
    Number_S SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES Person(userid) ON DELETE CASCADE,
    industry_name TEXT NOT NULL REFERENCES Industry(Name_industry) ON UPDATE CASCADE,
    Post TEXT NOT NULL REFERENCES Post(Name_post) ON UPDATE CASCADE,
    Salary_from NUMERIC CHECK(Salary_from <= Salary_to) NOT NULL,
    Salary_to NUMERIC CHECK(Salary_to >= Salary_from) NOT NULL,
    Experience TEXT NOT NULL,
    edType TEXT,
    edInst TEXT,
    Skills TEXT,
    Schedule TEXT NOT NULL,
    Date_summ TEXT NOT NULL,
    Rating INTEGER 
);

CREATE TABLE Vacancy(
    Number_V SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES Person(userid) ON DELETE CASCADE,
    industry_name TEXT NOT NULL REFERENCES Industry(Name_industry) ON UPDATE CASCADE,
    Post TEXT NOT NULL REFERENCES Post(Name_post) ON UPDATE CASCADE,
    about TEXT, 
    Salary_from NUMERIC CHECK(Salary_from <= Salary_to) NOT NULL,
    Salary_to NUMERIC CHECK(Salary_to >= Salary_from) NOT NULL,
    Exp_from TEXT,
    Conditions TEXT,
    Requirements TEXT,
    Duties TEXT,
    Schedule TEXT NOT NULL,
    Date_vac TEXT NOT NULL
);

CREATE TABLE View_summary(
    ID SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL,
    Number_S INTEGER NOT NULL,
    Date_view TEXT NOT NULL,
    Payment BIT(1),
    FOREIGN KEY(userid) REFERENCES Company(userid) ON DELETE CASCADE,
    FOREIGN KEY(Number_S) REFERENCES Summary(Number_S) ON DELETE CASCADE
);

CREATE TABLE View_vacancies(
    ID SERIAL PRIMARY KEY,
    Date_view TEXT NOT NULL,
    userid INTEGER NOT NULL,
    Number_V INTEGER NOT NULL,
    FOREIGN KEY(userid) REFERENCES Employee(userid) ON DELETE CASCADE,
    FOREIGN KEY(Number_V) REFERENCES Vacancy(Number_V) ON DELETE CASCADE
);

CREATE TABLE Otkliki(
    ID SERIAL PRIMARY KEY,
    Date_otklik TEXT NOT NULL,
    userid INTEGER NOT NULL,
    Number_V INTEGER NOT NULL,
    FOREIGN KEY(userid) REFERENCES Employee(userid) ON DELETE CASCADE,
    FOREIGN KEY(Number_V) REFERENCES Vacancy(Number_V) ON DELETE CASCADE
);

CREATE TABLE Customer(
    userid INTEGER PRIMARY KEY REFERENCES Person(userid) ON DELETE CASCADE,
    customer_name VARCHAR(255) NOT NULL,
    balance NUMERIC CHECK(Balance >= 0) NOT NULL,
    about TEXT
);

CREATE TABLE Area(
    area_name TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE Performer(
    userid INTEGER PRIMARY KEY REFERENCES Person(userid) ON DELETE CASCADE,
    performer_name TEXT NOT NULL,
    area_name TEXT NOT NULL REFERENCES Area(area_name) ON DELETE CASCADE,
    about TEXT NOT NULL
);

CREATE TABLE Task(
    task_id SERIAL PRIMARY KEY,
    userid INTEGER REFERENCES Person(userid) ON DELETE CASCADE,
    area_name TEXT NOT NULL REFERENCES Area(area_name) ON UPDATE CASCADE,
    about_task TEXT NOT NULL,
    date_task TEXT NOT NULL,
    cost INTEGER NOT NULL
);

CREATE TABLE Request(
    id SERIAL PRIMARY KEY,
    Date_req TEXT NOT NULL,
    userid INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    FOREIGN KEY(userid) REFERENCES Performer(userid) ON DELETE CASCADE,
    FOREIGN KEY(task_id) REFERENCES Task(task_id) ON DELETE CASCADE
);