--Will clear the whole database, be careful!!

\c testDatabase	
\set QUIT true
SET client_min_messages TO WARNING;
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
GRANT ALL ON SCHEMA public TO postgres;
\set QUIET false

------------------------------------------------------------------------------
CREATE TABLE UserData (
	userId SERIAL NOT NULL,
	ChalmersId TEXT UNIQUE NOT NULL,
	userEmail TEXT UNIQUE NOT NULL,
	passphrase BYTEA,
	verifiedAccount BOOLEAN NOT NULL DEFAULT FALSE,
	globalRole TEXT NOT NULL DEFAULT 'Student' CHECK (globalRole IN ('Student', 'Teacher')),
	fullName TEXT NOT NULL,
	PRIMARY KEY (userId),
	CHECK (userEmail ~* '^[a-zA-Z0-9.!#$%&''*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$')
	);


------------------------------------------------------------------------------
--USE courseId as foreign key in assignment files and lab tests,what should be used as primarykey?
CREATE TABLE Courses (
	courseId SERIAL PRIMARY KEY,
	courseName TEXT NOT NULL,
	courseCode Char(6) NOT NULL,
	teachingPeriod INTEGER NOT NULL,
	courseYear INTEGER NOT NULL,
	CHECK (teachingPeriod BETWEEN 1 AND 5),
	UNIQUE ( courseCode, teachingPeriod, courseYear)
);


------------------------------------------------------------------------------
CREATE TABLE Assignments(
	courseId SERIAL NOT NULL,
	assignmentId INTEGER NOT NULL CHECK (assignmentId > 0),
	endDate DATE NOT NULL,
	description TEXT NOT NULL DEFAULT '',
	assignmentName TEXT NOT NULL DEFAULT '',
	maxScore INT DEFAULT 1,
	passScore INT DEFAULT 1,
	PRIMARY KEY (courseId, assignmentId),
	CONSTRAINT constraint_courseid_fkey FOREIGN KEY (courseId) 
			REFERENCES Courses(courseId) 
			ON DELETE CASCADE 
			ON UPDATE CASCADE
);

CREATE OR REPLACE FUNCTION set_assignment_number_assignments()
RETURNS TRIGGER AS $$
DECLARE
    max_assignmentId INTEGER;
BEGIN
    IF NEW.assignmentId = 0 THEN
        SELECT COALESCE(MAX(assignmentId), 0) + 1 INTO max_assignmentId
        FROM Assignments
        WHERE courseId = NEW.courseId;
        IF max_assignmentId > 0 THEN
            NEW.assignmentId := max_assignmentId;
        ELSE
            SELECT COALESCE(MAX(assignmentId), 0) + 1 INTO NEW.assignmentId
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
	globalGroupId SERIAL PRIMARY KEY,
	groupNumberInCourse INTEGER NOT NULL,
	courseId INTEGER NOT NULL,
	UNIQUE (groupNumberInCourse, courseId),
	CONSTRAINT constraint_courseid_fkey FOREIGN KEY (courseId) 
	REFERENCES Courses(courseId) 
	ON DELETE CASCADE
	ON UPDATE CASCADE
);


------------------------------------------------------------------------------
--for unittests
CREATE TABLE PythonTestFiles (
	courseId SERIAL NOT NULL,
	assignmentId INTEGER NOT NULL, 
	testFileName TEXT NOT NULL,
	fileData BYTEA NOT NULL,
	PRIMARY KEY(courseId, assignmentId, testFileName),
	CONSTRAINT constraint_assignment_course_fkey FOREIGN KEY (courseId, assignmentId) 
		REFERENCES Assignments(courseId, assignmentId) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE
);


------------------------------------------------------------------------------
CREATE TABLE RequiredFileNames (
	courseId SERIAL NOT NULL,
	assignmentId INTEGER NOT NULL, 
	assignmentFileName TEXT NOT NULL,
	PRIMARY KEY (courseId, assignmentId, assignmentFileName),
	CONSTRAINT constraint_assignment_course_fkey FOREIGN KEY (courseId, assignmentId) 
		REFERENCES Assignments(courseId, assignmentId) 
		ON UPDATE CASCADE 
		ON DELETE CASCADE
);


------------------------------------------
CREATE TABLE SubmissionFeedback (
    globalGroupId INTEGER NOT NULL,
    courseId SERIAL NOT NULL,  
    assignmentId INTEGER NOT NULL,
    submissionNumber SERIAL NOT NULL,
    automaticFeedback JSON,
    teacherFeedback TEXT,
    testPassed BOOLEAN NOT NULL DEFAULT FALSE,
    teacherGrade BOOLEAN,
	feedbackDate TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'),
	createdDate TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'),
	assignmentScore INT DEFAULT 0,
	userId INT,
    PRIMARY KEY (globalGroupId, courseId, assignmentId, submissionNumber),
    CONSTRAINT constraint_groupid_fkey FOREIGN KEY (globalGroupId)
        REFERENCES Groups(globalGroupId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT constraint_assignment_course_fkey FOREIGN KEY (courseId, assignmentId)
        REFERENCES Assignments(courseId, assignmentId)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
	CONSTRAINT constraint_userId_fkey FOREIGN KEY (userId)
		REFERENCES UserData(userId)
		ON DELETE CASCADE
		ON UPDATE CASCADE	
);

CREATE OR REPLACE FUNCTION set_submission_number_SubmissionFeedback()
RETURNS TRIGGER AS $$
DECLARE
    max_submissionNumber INTEGER;
BEGIN
    IF NEW.submissionNumber = 0 THEN
        SELECT COUNT(submissionNumber) + 1 INTO max_submissionNumber
        FROM SubmissionFeedback
        WHERE globalGroupId = NEW.globalGroupId
            AND courseId = NEW.courseId
            AND assignmentId = NEW.assignmentId;
        IF submissionNumber > 0 THEN
            NEW.submissionNumber := max_submissionNumber;
        ELSE
            SELECT COUNT(submissionNumber) + 1 INTO NEW.submissionNumber
            FROM SubmissionFeedback
            WHERE globalGroupId = NEW.globalGroupId
                AND courseId = NEW.courseId
                AND assignmentId = NEW.assignmentId;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER increment_submission_SubmissionFeedback
BEFORE INSERT ON SubmissionFeedback
FOR EACH ROW
EXECUTE FUNCTION set_submission_number_SubmissionFeedback();


------------------------------------------------------------------------------
CREATE TABLE SubmittedAssignment (
		globalGroupId INTEGER NOT NULL, 
		courseId SERIAL NOT NULL,
		assignmentId INTEGER NOT NULL,
		submissionNumber SERIAL NOT NULL,
		assignmentFileName TEXT NOT NULL, 
		fileData BYTEA NOT NULL, 
		submissionDate TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT (CURRENT_TIMESTAMP AT TIME ZONE 'Europe/Stockholm'), 
		PRIMARY KEY(globalGroupId, courseId, assignmentId, assignmentFileName, submissionNumber),
		CONSTRAINT constraint_groupid_fkey FOREIGN KEY (globalGroupId) 
			REFERENCES Groups (globalGroupId) 
			ON DELETE CASCADE 
			ON UPDATE CASCADE,
		CONSTRAINT constraint_filename_assignment_course_fkey 
			FOREIGN KEY (assignmentFileName, courseId, assignmentId) 
			REFERENCES RequiredFileNames(assignmentFileName, courseId, assignmentId) 
			ON DELETE CASCADE 
			ON UPDATE CASCADE
	);

CREATE OR REPLACE FUNCTION set_submission_number_SubmittedAssignment()
RETURNS TRIGGER AS $$
DECLARE
    max_submissionNumber INTEGER;
BEGIN
    IF NEW.submissionNumber = 0 THEN
        SELECT COUNT(submissionNumber) + 1 INTO max_submissionNumber
        FROM SubmittedAssignment
        WHERE groupId = NEW.groupId
            AND courseId = NEW.courseId
            AND assignmentId = NEW.assignmentId
            AND assignmentFileName = NEW.assignmentFileName;
        IF max_submissionNumber > 0 THEN
            NEW.submissionNumber := max_submissionNumber;
        ELSE
            SELECT COUNT(submissionNumber) + 1 INTO NEW.submissionNumber
            FROM SubmittedAssignment
            WHERE groupId = NEW.groupId
                AND courseId = NEW.courseId
                AND assignmentId = NEW.assignmentId
                AND assignmentFileName = NEW.assignmentFileName;
        END IF;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE TRIGGER increment_submission_SubmittedAssignment
BEFORE INSERT ON SubmittedAssignment
FOR EACH ROW
EXECUTE FUNCTION set_submission_number_SubmittedAssignment();


------------------------------------------------------------------------------
CREATE TABLE UserInGroup (
	userId INTEGER,
	globalGroupId INTEGER,
	PRIMARY KEY (userId, globalGroupId),
	CONSTRAINT constraint_groupid_fkey FOREIGN KEY (globalGroupId) 
		REFERENCES Groups(globalGroupId) 
		ON DELETE CASCADE 
		ON UPDATE CASCADE,
	CONSTRAINT constraint_userid_fkey FOREIGN KEY (userId) 
		REFERENCES UserData(userId) 
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
SELECT userCourse.userId, userCourse.userRole, course.courseId, course.courseName, course.courseCode, course.teachingPeriod, course.courseYear
FROM UserInCourse userCourse
JOIN Courses course ON userCourse.courseId = course.courseId;

------------------------------------------------------------------------------
--This view shows user and its courses with corresponding groups. Useful to get group info if user and course id is known

CREATE OR REPLACE VIEW UserGroupCourseInfo AS
SELECT userGroup.userId, userGroup.globalGroupId, grp.groupNumberInCourse, grp.courseId 
	AS courseId, course.courseCode, course.courseYear, course.teachingPeriod
FROM UserInGroup userGroup
JOIN Groups grp ON userGroup.globalGroupId = grp.globalGroupId
JOIN Courses course ON grp.courseId = course.courseId;

------------------------------------------------------------------------------
--This view shows all user and group information, eg. used to get all groupmember cids from your group 
CREATE OR REPLACE VIEW UserGroupInfo AS
SELECT UserData.userId, UserData.chalmersId, UserInGroup.globalGroupId, Groups.groupNumberInCourse
FROM UserData
JOIN UserInGroup ON UserData.userId = UserInGroup.userId
JOIN Groups ON UserInGroup.globalGroupId = Groups.globalGroupId;

------------------------------------------------------------------------------
CREATE VIEW GroupDetails AS
SELECT grp.globalGroupId, grp.groupNumberInCourse, grp.courseId, users.fullName
FROM Groups grp
LEFT JOIN UserInGroup userGroup ON grp.globalGroupId = userGroup.globalGroupId
LEFT JOIN UserData users ON userGroup.userId = users.userId;