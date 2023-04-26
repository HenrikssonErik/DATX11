--Will clear the whole database, be careful!!
/*
\c hydrant	
\set QUIT true
SET client_min_messages TO WARNING;
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
\set QUIET false
*/
------------------------------------------------------------------------------
CREATE TABLE UserData (
	userId SERIAL NOT NULL,
	cid TEXT UNIQUE NOT NULL,
	email TEXT UNIQUE NOT NULL,
	passphrase BYTEA,
	verified BOOLEAN NOT NULL DEFAULT FALSE,
	globalRole TEXT NOT NULL DEFAULT 'Student' CHECK (globalRole IN ('Student', 'Teacher', 'Admin')),
	fullName TEXT NOT NULL,
	PRIMARY KEY (userId),
	CHECK (email ~* '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$')
	);


------------------------------------------------------------------------------
--USE courseId as foreign key in assignment files and lab tests,what should be used as primarykey?
CREATE TABLE Courses (
	courseId SERIAL PRIMARY KEY,
	courseName TEXT NOT NULL,
	course Char(6) NOT NULL,
	teachingPeriod INTEGER NOT NULL,
	courseYear INTEGER NOT NULL,
	CHECK (teachingPeriod BETWEEN 1 AND 5),
	UNIQUE ( course, teachingPeriod, courseYear)
);


------------------------------------------------------------------------------
CREATE TABLE Assignments(
	courseId SERIAL NOT NULL,
	assignment INTEGER NOT NULL CHECK (assignment > 0),
	endDate DATE NOT NULL,
	description TEXT NOT NULL DEFAULT '',
	name TEXT NOT NULL DEFAULT '',
	maxScore INT DEFAULT 1,
	passScore INT DEFAULT 1,
	PRIMARY KEY (courseId, assignment),
	CONSTRAINT constraint_courseid_fkey FOREIGN KEY (courseId) 
			REFERENCES Courses(courseId) 
			ON DELETE CASCADE 
			ON UPDATE CASCADE
);

CREATE OR REPLACE FUNCTION set_assignment_number_assignments()
RETURNS TRIGGER AS $$
DECLARE
    max_assignment INTEGER;
BEGIN
    IF NEW.assignment = 0 THEN
        SELECT COALESCE(MAX(assignment), 0) + 1 INTO max_assignment
        FROM Assignments
        WHERE courseId = NEW.courseId;
        IF max_assignment > 0 THEN
            NEW.assignment := max_assignment;
        ELSE
            SELECT COALESCE(MAX(assignment), 0) + 1 INTO NEW.assignment
            FROM Assignments
            WHERE courseId = NEW.courseId;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER increment_assignment_assignments
BEFORE INSERT ON Assignments
FOR EACH ROW
EXECUTE FUNCTION set_assignment_number_assignments();


------------------------------------------------------------------------------
CREATE TABLE Groups (
	groupId SERIAL PRIMARY KEY,
	groupNumber INTEGER NOT NULL,
	course INTEGER NOT NULL,
	UNIQUE (groupNumber, course),
	CONSTRAINT constraint_courseid_fkey FOREIGN KEY (course) 
	REFERENCES Courses(courseid) 
	ON DELETE CASCADE
	ON UPDATE CASCADE
);


------------------------------------------------------------------------------
--for unittests
CREATE TABLE TestFiles (
	courseId SERIAL NOT NULL,
	assignment INTEGER NOT NULL, 
	filename TEXT NOT NULL,
	fileData BYTEA NOT NULL,
	PRIMARY KEY(courseId, assignment, fileName),
	CONSTRAINT constraint_assignment_course_fkey FOREIGN KEY (courseId, assignment) 
		REFERENCES Assignments(courseId, assignment) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE
);


------------------------------------------------------------------------------
CREATE TABLE FileNames (
	nameId SERIAL NOT NULL,
	courseId SERIAL NOT NULL,
	assignment INTEGER NOT NULL, 
	filename TEXT NOT NULL,
	UNIQUE (courseId, assignment, filename),
	PRIMARY KEY(nameId),
	CONSTRAINT constraint_assignment_course_fkey FOREIGN KEY (courseId, assignment) 
		REFERENCES Assignments(courseId, assignment) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE
);


------------------------------------------
CREATE TABLE AssignmentFeedback (
    groupId INTEGER NOT NULL,
    courseId SERIAL NOT NULL,  
    assignment INTEGER NOT NULL,
    submission SERIAL NOT NULL,
    testFeedback JSON,
    teacherFeedback TEXT,
    testPass BOOLEAN NOT NULL DEFAULT FALSE,
    teacherGrade BOOLEAN,
	feedbackDate TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'),
	createdDate TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'),
	score INT DEFAULT 0,
	userId INT,
    PRIMARY KEY (groupId, courseId, assignment, submission),
    CONSTRAINT constraint_groupid_fkey FOREIGN KEY (groupId)
        REFERENCES groups(groupId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT constraint_assignment_course_fkey FOREIGN KEY (courseId, assignment)
        REFERENCES assignments(courseid, assignment)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	CONSTRAINT constraint_userId_fkey FOREIGN KEY (userId)
		REFERENCES userdata(userId)
		ON DELETE CASCADE
		ON UPDATE CASCADE	
);

CREATE OR REPLACE FUNCTION set_submission_number_assignmentfeedback()
RETURNS TRIGGER AS $$
DECLARE
    max_submission INTEGER;
BEGIN
    IF NEW.submission = 0 THEN
        SELECT COUNT(submission) + 1 INTO max_submission
        FROM AssignmentFeedback
        WHERE groupId = NEW.groupId
            AND courseId = NEW.courseId
            AND assignment = NEW.assignment;
        IF max_submission > 0 THEN
            NEW.submission := max_submission;
        ELSE
            SELECT COUNT(submission) + 1 INTO NEW.submission
            FROM AssignmentFeedback
            WHERE groupId = NEW.groupId
                AND courseId = NEW.courseId
                AND assignment = NEW.assignment;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER increment_submission_assignmentfeedback
BEFORE INSERT ON AssignmentFeedback
FOR EACH ROW
EXECUTE FUNCTION set_submission_number_assignmentfeedback();


------------------------------------------------------------------------------
CREATE TABLE AssignmentFiles (
		groupId INTEGER NOT NULL, 
		courseId SERIAL NOT NULL,
		assignment INTEGER NOT NULL,
		submission SERIAL NOT NULL,
		fileName TEXT NOT NULL, --Could add foregin key to FileName-table
		fileData BYTEA NOT NULL, 
		submissionDate TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'), 
		PRIMARY KEY(groupId, courseId, assignment, fileName, submission),
		CONSTRAINT constraint_groupid_fkey FOREIGN KEY (groupId) 
			REFERENCES Groups (groupId) 
			ON DELETE CASCADE 
			ON UPDATE CASCADE,
		CONSTRAINT constraint_filename_assignment_course_fkey 
			FOREIGN KEY (filename, courseid, assignment) 
			REFERENCES filenames(filename, courseid, assignment) 
			ON DELETE CASCADE 
			ON UPDATE CASCADE
	);

CREATE OR REPLACE FUNCTION set_submission_number_assignmentfiles()
RETURNS TRIGGER AS $$
DECLARE
    max_submission INTEGER;
BEGIN
    IF NEW.submission = 0 THEN
        SELECT COUNT(submission) + 1 INTO max_submission
        FROM AssignmentFiles
        WHERE groupId = NEW.groupId
            AND courseId = NEW.courseId
            AND assignment = NEW.assignment
            AND fileName = NEW.fileName;
        IF max_submission > 0 THEN
            NEW.submission := max_submission;
        ELSE
            SELECT COUNT(submission) + 1 INTO NEW.submission
            FROM AssignmentFiles
            WHERE groupId = NEW.groupId
                AND courseId = NEW.courseId
                AND assignment = NEW.assignment
                AND fileName = NEW.fileName;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER increment_submission_assignmentfiles
BEFORE INSERT ON AssignmentFiles
FOR EACH ROW
EXECUTE FUNCTION set_submission_number_assignmentfiles();


------------------------------------------------------------------------------
CREATE TABLE UserInGroup (
	userId INTEGER,
	groupId INTEGER,
	PRIMARY KEY (userId, groupId),
	CONSTRAINT constraint_groupid_fkey FOREIGN KEY (groupId) 
		REFERENCES Groups(groupId) 
		ON DELETE CASCADE 
		ON UPDATE CASCADE,
	CONSTRAINT constraint_userid_fkey FOREIGN KEY (userId) 
		REFERENCES Userdata(userId) 
		ON DELETE CASCADE 
		ON UPDATE CASCADE
);


------------------------------------------------------------------------------
CREATE TABLE UserInCourse (
	userId INTEGER,
	courseId INTEGER,
	userRole TEXT NOT NULL CHECK (userRole IN ('Admin', 'Teacher', 'Student')),
	PRIMARY KEY (userId, courseId),
		CONSTRAINT constraint_courseid_fkey FOREIGN KEY (courseId) 
		REFERENCES Courses(courseId) 
		ON DELETE CASCADE 
		ON UPDATE CASCADE,
	CONSTRAINT constraint_userid_fkey FOREIGN KEY (userId) 
		REFERENCES Userdata(userId) 
		ON DELETE CASCADE 
		ON UPDATE CASCADE
);


------------------------------------------------------------------------------
--View for user and course data can be called for course inf from specific user:
--To Call do: select * from user_course_info where userId = 'id int';

CREATE OR REPLACE VIEW UserCourseInfo AS
SELECT uic.userId, uic.userRole, c.courseId, c.courseName, c.course, c.teachingPeriod, c.courseYear
FROM UserInCourse uic
JOIN Courses c ON uic.courseId = c.courseId;

------------------------------------------------------------------------------
--This view shows user and its courses with corresponding groups. Useful to get group info if user and course id is known

CREATE OR REPLACE VIEW UserGroupCourseInfo AS
SELECT uig.userId, uig.groupId, g.groupNumber, g.course AS courseId, c.course, c.courseYear, c.teachingPeriod
FROM UserInGroup uig
JOIN Groups g ON uig.groupId = g.groupId
JOIN Courses c ON g.course = c.courseId;

------------------------------------------------------------------------------
--This view shows all user and group information, eg. used to get all groupmember cids from your group 
CREATE OR REPLACE VIEW UserGroupInfo AS
SELECT UserData.userId, UserData.cid, UserInGroup.groupId, Groups.groupNumber
FROM UserData
JOIN UserInGroup ON UserData.userId = UserInGroup.userId
JOIN Groups ON UserInGroup.groupId = Groups.groupId;

------------------------------------------------------------------------------
CREATE VIEW GroupDetails AS
SELECT g.groupid, g.groupnumber, g.course, u.fullname
FROM Groups g
LEFT JOIN UserInGroup uig ON g.groupid = uig.groupid
LEFT JOIN UserData u ON uig.userid = u.userid;