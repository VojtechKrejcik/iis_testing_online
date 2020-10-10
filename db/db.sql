CREATE DATABASE IF NOT EXISTS `iis`;
USE `iis`;

CREATE TABLE IF NOT EXISTS `accounts` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `username` varchar(50) NOT NULL,
      `password` varchar(255) NOT NULL,
      `name` varchar(20) NOT NULL,
      `surname` varchar(20) NOT NULL,
      `email` varchar(100) NOT NULL,
      `status` varchar(10) NOT NULL,
    PRIMARY KEY (`id`)
);

CREATE TABLE IF NOT EXISTS `test_template` (
      `test_id` int(11) NOT NULL AUTO_INCREMENT,
      `active_from` DATETIME NOT NULL,
      `active to` DATETIME NOT NULL,
      `creator` int DEFAULT null,

      ADD CONSTRAINT "creator_fk" 
      FOREIGN KEY ("creator") REFERENCES "accounts"("id")
      PRIMARY KEY (`test_id`)

);

CREATE TABLE IF NOT EXISTS `test_assigned` (
     `assigned_test_id` int(11) not null,
     `template_test_id` int(11) not null,
     `student_id` int(11) not null,
     `score` int(11)
     `subbed` TIMESTAMP,
     ADD CONSTRAINT "template_test_id_fk" 
      FOREIGN KEY ("template_test_id") REFERENCES "test_template"("test_id")

    ADD CONSTRAINT "student_id_fk" 
      FOREIGN KEY ("student_id") REFERENCES "accounts"("id")

     PRIMARY KEY (`test_id`)
     

);
CREATE TABLE IF NOT EXISTS `assistent_test` (
      `assisten_id` int(11) NOT NULL,
      `test_id` int(11) NOT NULL,
    ADD CONSTRAINT "assigned_test_id_fk" 
      FOREIGN KEY ("test_id") REFERENCES "test_assigned"("assigned_test_id")

    ADD CONSTRAINT "assitent_id_fk" 
      FOREIGN KEY ("assistent_id") REFERENCES "accounts"("id")
      PRIMARY KEY (`assistent_id`, `test_id`)
);


INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (2, 'admin', 'admin', 'name', 'surname','test@test.com','admin');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (3, 'student', 'student', 'name', 'surname','test@test.com','student');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (4, 'assistent', 'assistent', 'name', 'surname','test@test.com','assistent');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (5, 'profesor', 'profesor', 'name', 'surname','test@test.com','profesor');
