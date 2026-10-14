-- =========================================================
-- SI PENGADU - Database Dump for phpMyAdmin / MySQL
-- Sistem Pengaduan Mahasiswa Prodi Teknik Informatika
-- Universitas Pahlawan Tuanku Tambusai
-- =========================================================

SET FOREIGN_KEY_CHECKS = 0;
CREATE DATABASE IF NOT EXISTS `si_pengaduan` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `si_pengaduan`;

-- Table structure for `attachments`
DROP TABLE IF EXISTS `attachments`;
CREATE TABLE `attachments` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `complaint_id` int(11) NOT NULL,
  `filename` varchar(200) NOT NULL,
  `original_filename` varchar(200) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `file_size` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `complaint_id` (`complaint_id`),
  CONSTRAINT `attachments_ibfk_1` FOREIGN KEY (`complaint_id`) REFERENCES `complaints` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for `complaint_responses`
DROP TABLE IF EXISTS `complaint_responses`;
CREATE TABLE `complaint_responses` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `complaint_id` int(11) NOT NULL,
  `responder_name` varchar(100) NOT NULL,
  `message` text NOT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `complaint_id` (`complaint_id`),
  CONSTRAINT `complaint_responses_ibfk_1` FOREIGN KEY (`complaint_id`) REFERENCES `complaints` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for `complaints`
DROP TABLE IF EXISTS `complaints`;
CREATE TABLE `complaints` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `ticket_number` varchar(20) NOT NULL,
  `title` varchar(200) NOT NULL,
  `description` text NOT NULL,
  `category` varchar(50) NOT NULL,
  `status` varchar(20) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ticket_number` (`ticket_number`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `complaints_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for `notifications`
DROP TABLE IF EXISTS `notifications`;
CREATE TABLE `notifications` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(200) NOT NULL,
  `message` text NOT NULL,
  `type` varchar(50) DEFAULT NULL,
  `is_read` tinyint(1) DEFAULT NULL,
  `complaint_id` int(11) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `complaint_id` (`complaint_id`),
  CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `notifications_ibfk_2` FOREIGN KEY (`complaint_id`) REFERENCES `complaints` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for `status_logs`
DROP TABLE IF EXISTS `status_logs`;
CREATE TABLE `status_logs` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `complaint_id` int(11) NOT NULL,
  `old_status` varchar(20) DEFAULT NULL,
  `new_status` varchar(20) NOT NULL,
  `note` varchar(200) DEFAULT NULL,
  `changed_by` varchar(100) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `complaint_id` (`complaint_id`),
  CONSTRAINT `status_logs_ibfk_1` FOREIGN KEY (`complaint_id`) REFERENCES `complaints` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table structure for `users`
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `password_hash` varchar(256) NOT NULL,
  `full_name` varchar(100) NOT NULL,
  `nim` varchar(20) NOT NULL,
  `program_studi` varchar(100) DEFAULT NULL,
  `semester` int(11) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `avatar` varchar(200) DEFAULT NULL,
  `created_at` datetime DEFAULT NULL,
  `updated_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `nim` (`nim`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Dumping data for `users`
INSERT INTO `users` (`id`, `email`, `password_hash`, `full_name`, `nim`, `program_studi`, `semester`, `phone`, `avatar`, `created_at`, `updated_at`) VALUES (1, 'agamal2455201016.mhs@universitaspahlawan.ac.id', 'scrypt:32768:8:1$aepAVyhzlKe4eLJf$9e40f35a04ccf06fedce89780c66b4128fc365a7ea091d5fafab89373d60cbfb1d7761c0f427721689d9aa16dccb38bff5a83568d553c88d0fd496c0b41e8fee', 'Agam Al Hakim Hasibuan', '2455201016', 'Teknik Informatika', 5, '08123456789', 'avatar_1_e4e46e11.png', '2026-10-13 16:43:08', '2026-10-13 20:08:01');
INSERT INTO `users` (`id`, `email`, `password_hash`, `full_name`, `nim`, `program_studi`, `semester`, `phone`, `avatar`, `created_at`, `updated_at`) VALUES (2, 'agam@student.ti.ac.id', 'scrypt:32768:8:1$njfKtGnyCoE15RYP$97296c341755a068c429d1bc757fe18e9801628cb84412eb173eddc0d6e2bc12ecbbbe8e35ab219568b8e423e43f3411ef4afb0e6b84ef1a8e4562823ef3f042', 'iyad', '2455201002', 'Teknik Informatika', 5, NULL, NULL, '2026-10-13 20:36:50', '2026-10-13 20:36:50');

SET FOREIGN_KEY_CHECKS = 1;