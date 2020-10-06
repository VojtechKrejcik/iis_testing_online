CREATE DATABASE IF NOT EXISTS `iis`;
USE `iis`;

CREATE TABLE IF NOT EXISTS `accounts` (
      `id` int(11) NOT NULL AUTO_INCREMENT,
      `username` varchar(50) NOT NULL,
      `password` varchar(255) NOT NULL,
      `email` varchar(100) NOT NULL,
      `status` varchar(10) NOT NULL,
    PRIMARY KEY (`id`)
);

INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (2, 'admin', 'admin', 'test@test.com','admin');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (3, 'student', 'student', 'test@test.com','student');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (4, 'assistent', 'assistent', 'test@test.com','assistent');
INSERT INTO `accounts` (`id`, `username`, `password`, `email`, `status`) VALUES (5, 'profesor', 'profesor', 'test@test.com','profesor');
