-- =======================================================
-- AyuCare Database Schema
-- Project: आयुCare (AyuCare) - Smart Symptom Guidance & Specialist Recommendation
-- Compatible with MySQL 5.7+ / 8.0+ & MySQL Workbench
-- =======================================================

CREATE DATABASE IF NOT EXISTS `ayucare_db` 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE `ayucare_db`;

-- 1. Patients Table
CREATE TABLE IF NOT EXISTS `patients` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `mobile` VARCHAR(20) NOT NULL UNIQUE,
    `age` INT NOT NULL,
    `gender` VARCHAR(20) DEFAULT 'Not Specified',
    `password_hash` VARCHAR(255) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Specialists Table
CREATE TABLE IF NOT EXISTS `specialists` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `description` TEXT NOT NULL,
    `common_conditions` TEXT NOT NULL,
    `icon` VARCHAR(50) DEFAULT 'fa-user-doctor'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Doctors Table
CREATE TABLE IF NOT EXISTS `doctors` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `full_name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `mobile` VARCHAR(20) NOT NULL UNIQUE,
    `specialization` VARCHAR(100) NOT NULL,
    `registration_number` VARCHAR(100) NOT NULL UNIQUE,
    `password_hash` VARCHAR(255) NOT NULL,
    `verification_status` ENUM('pending', 'verified', 'rejected') DEFAULT 'pending',
    `bio` TEXT,
    `experience_years` INT DEFAULT 0,
    `hospital_clinic` VARCHAR(150),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Symptoms Table
CREATE TABLE IF NOT EXISTS `symptoms` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL UNIQUE,
    `category` VARCHAR(50) NOT NULL,
    `description` TEXT NOT NULL,
    `urgency_level` ENUM('Mild', 'Moderate', 'Severe/Emergency') DEFAULT 'Mild',
    `warning_signs` TEXT,
    `specialist_id` INT,
    CONSTRAINT `fk_symptom_specialist` FOREIGN KEY (`specialist_id`) REFERENCES `specialists`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Symptom Guidance Table
CREATE TABLE IF NOT EXISTS `symptom_guidance` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `symptom_id` INT NOT NULL,
    `preliminary_guidance` TEXT NOT NULL,
    `mild_home_care` TEXT, -- Only for safe mild symptoms; empty or null when home care is not clinically appropriate
    `warning_signs_details` TEXT,
    `reference_source` VARCHAR(255) DEFAULT 'WHO / Mayo Clinic Guidelines',
    CONSTRAINT `fk_guidance_symptom` FOREIGN KEY (`symptom_id`) REFERENCES `symptoms`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Consultations Table
CREATE TABLE IF NOT EXISTS `consultations` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `doctor_id` INT NOT NULL,
    `symptom_summary` TEXT,
    `preferred_date` DATE,
    `preferred_time` VARCHAR(50),
    `notes` TEXT,
    `status` ENUM('Pending', 'Accepted', 'Rejected', 'Completed') DEFAULT 'Pending',
    `doctor_notes` TEXT,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT `fk_consultation_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_consultation_doctor` FOREIGN KEY (`doctor_id`) REFERENCES `doctors`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 7. Symptom History Table (Patient Submissions)
CREATE TABLE IF NOT EXISTS `symptom_history` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `patient_id` INT NOT NULL,
    `symptom_name` VARCHAR(100) NOT NULL,
    `duration` VARCHAR(100) NOT NULL,
    `severity` ENUM('Mild', 'Moderate', 'Severe') NOT NULL,
    `description` TEXT,
    `additional_details` TEXT,
    `is_emergency` BOOLEAN DEFAULT FALSE,
    `guidance_summary` TEXT,
    `home_care_summary` TEXT,
    `recommended_specialist` VARCHAR(100),
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_history_patient` FOREIGN KEY (`patient_id`) REFERENCES `patients`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 8. Chatbot FAQs Table
CREATE TABLE IF NOT EXISTS `chatbot_faqs` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `category` VARCHAR(50) NOT NULL,
    `keywords` TEXT NOT NULL,
    `question` VARCHAR(255) NOT NULL,
    `answer` TEXT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 9. Contact & Feedback Messages Table
CREATE TABLE IF NOT EXISTS `contact_messages` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(100) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `subject` VARCHAR(150) NOT NULL,
    `message` TEXT NOT NULL,
    `feedback_type` VARCHAR(50) DEFAULT 'General Inquiry',
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 10. Mobile OTP Verification Table
CREATE TABLE IF NOT EXISTS `mobile_otps` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `mobile` VARCHAR(20) NOT NULL,
    `otp_code` VARCHAR(10) NOT NULL,
    `purpose` VARCHAR(30) DEFAULT 'registration',
    `is_verified` BOOLEAN DEFAULT FALSE,
    `attempts` INT DEFAULT 0,
    `expires_at` TIMESTAMP NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 11. Password Resets Table
CREATE TABLE IF NOT EXISTS `password_resets` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `role` VARCHAR(20) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `token` VARCHAR(128) NOT NULL UNIQUE,
    `expires_at` TIMESTAMP NOT NULL,
    `is_used` BOOLEAN DEFAULT FALSE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Indexes for performance
CREATE INDEX `idx_patient_email` ON `patients` (`email`);
CREATE INDEX `idx_doctor_email` ON `doctors` (`email`);
CREATE INDEX `idx_symptom_name` ON `symptoms` (`name`);
CREATE INDEX `idx_consultation_patient` ON `consultations` (`patient_id`);
CREATE INDEX `idx_consultation_doctor` ON `consultations` (`doctor_id`);
CREATE INDEX `idx_history_patient` ON `symptom_history` (`patient_id`);
CREATE INDEX `idx_mobile_otps` ON `mobile_otps` (`mobile`, `purpose`);
CREATE INDEX `idx_password_resets_token` ON `password_resets` (`token`);
