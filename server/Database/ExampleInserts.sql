INSERT INTO userdata (userid, chalmersid, useremail, passphrase, verifiedaccount, globalrole, fullname) VALUES
    (9, 'gabhags', 'gabhags@chalmers.se', E'\\x24326224313224356b4f33665a33715639586c5a443946675a35755465712e65466a59467965623036794d6b535453545732793359657a6b676e564b', 't', 'Admin', 'Gabriel Hagström'),
    (4, 'testadmin', 'testadmin@chalmers.se', E'\\x243262243132244a4d486b662e6153647a4b6f50623059737942534265337757375a454d367542324e6b4244336f4a386c4b443445776d6865786475', 't', 'Admin', 'Test Adminsson'),
    (10, 'maltec', 'maltec@chalmers.se', E'\\x243262243132243545727434394b31734747474352396477734b386d65305a684f694435734636314b695932334a6a74534a725a344b7a304a335775', 't', 'Student', 'Malte Carlstedt'),
    (5, 'teststudent', 'teststudent@chalmers.se', E'\\x243262243132244a4d486b662e6153647a4b6f50623059737942534265337757375a454d367542324e6b4244336f4a386c4b443445776d6865786475', 't', 'Student', 'Test Studentsson'),
    (2, 'alebru', 'alebru@chalmers.se', E'\\x24326224313224642f476e6275536c4d6867647166555850306c504d2e73385574474b55745949436a476b436a6b504b794755453273486735573965', 't', 'Student', 'Alexander Brunnegård'),
    (8, 'erhen', 'erhen@chalmers.se', E'\\x24326224313224473055716b343675562e5353712e6f3466372e4f6a2e6d30317a4b375a545a534174476b442e627676676458332e5a7356574a7636', 't', 'Student', 'Erik Henriksson'),
    (1, 'kvalden', 'kvalden@chalmers.se', E'\\x24326224313224485734713276736a563934306355795350454b65342e6234716f625847507157553746724751306c664672424a56632f464a474575', 't', 'Admin', 'Sebastian Kvaldén');


INSERT INTO courses (courseid, coursename, coursecode, teachingperiod, courseyear)
VALUES (1, 'Test Course 1', 'TES123', 1, 2024),
       (5, 'Test course 2', 'TES111', 1, 2024),
       (6, 'Introduction to why Boras is not a real city', 'BOR123', 4, 2023),
       (9, 'DEMO', 'DEM123', 4, 2023),
       (10, 'test course 5', 'TES567', 3, 2024),
       (11, 'Introduction to Basic Python', 'PYT123', 5, 2023);

INSERT INTO groups (globalgroupid, groupnumberincourse, courseid)
VALUES
(16, 2, 1),
(19, 1, 6),
(25, 1, 9),
(27, 3, 1);