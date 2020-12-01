DROP DATABASE `iis`;
CREATE DATABASE IF NOT EXISTS `iis`;
USE `iis`;

CREATE TABLE IF NOT EXISTS `accounts` (
	`id` int(11) NOT NULL AUTO_INCREMENT,
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
	`active_to` DATETIME NOT NULL,
	`creator` int DEFAULT null,
	`file` varchar(255) DEFAULT null,


	CONSTRAINT `creator_fk` FOREIGN KEY (`creator`)
		REFERENCES `accounts`(`id`),
	PRIMARY KEY (`test_id`)
);
     
CREATE TABLE IF NOT EXISTS `registrations` (
	`person_id` int(11) NOT NULL,
	`person_type` varchar(10) NOT NULL,
	`test_id` int(11) NOT NULL,
	`test_copy` varchar(255) DEFAULT null,
	`approved` int(1) NOT NULL,
	`score` int(10) NOT NULL,

	CONSTRAINT `person_id_fk` FOREIGN KEY (`person_id`) 
		REFERENCES `accounts`(`id`),
	CONSTRAINT `test_id_fk` FOREIGN KEY (`test_id`) 
		REFERENCES `test_template`(`test_id`),
		
	PRIMARY KEY (`person_id`, `test_id`)
);

INSERT INTO `accounts` (`password`, `name`, `surname`, `email`, `status`) VALUES ('prdel', 'Pepik', 'Prdelka', 'admin@test.com','admin');
INSERT INTO `accounts` (`password`, `name`, `surname`, `email`, `status`) VALUES ('prdel', 'Ondra', 'Ouvajs', 'student@test.com','student');
INSERT INTO `accounts` (`password`, `name`, `surname`, `email`, `status`) VALUES ('prdel', 'Karel', 'Karotka', 'assistent@test.com','assistent');
INSERT INTO `accounts` (`password`, `name`, `surname`, `email`, `status`) VALUES ('prdel', 'Tonda', 'Tupec', 'profesor@test.com','profesor');
