-- ====================================================================
-- Complete Database Schema for Spamwatch.ai Project
-- ====================================================================
-- This SQL script creates the complete database structure for the
-- Spamwatch.ai web application, including all necessary tables,
-- relationships, indexes, and sample data for testing.
--
-- The database supports:
-- - User authentication and session management
-- - Tool usage tracking and analytics
-- - Detailed result storage for spam text, deepfake image, and deepfake video analysis
-- - Proper foreign key relationships and indexing for performance
--
-- Database: MySQL (compatible with MariaDB)
-- Character Set: UTF-8 (default)
-- ====================================================================

-- ====================================================================
-- TABLE DROPS (Cleanup existing tables if they exist)
-- ====================================================================
-- Drop tables in reverse dependency order to avoid foreign key conflicts
DROP TABLE IF EXISTS user_sessions;
DROP TABLE IF EXISTS tool_usage;
DROP TABLE IF EXISTS deepfake_image_results;
DROP TABLE IF EXISTS deepfake_video_results;
DROP TABLE IF EXISTS spam_text_results;
DROP TABLE IF EXISTS users;

-- ====================================================================
-- USERS TABLE
-- ====================================================================
-- Core user table storing authentication information
-- This table was missing from the original schema and is essential
-- for user management functionality
CREATE TABLE IF NOT EXISTS users (
    email VARCHAR(255) PRIMARY KEY,                    -- Primary key: User email address
    password_hash VARCHAR(255) NOT NULL,               -- Securely hashed password using bcrypt
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,     -- Account creation timestamp
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  -- Last update timestamp
);

-- ====================================================================
-- USER_SESSIONS TABLE
-- ====================================================================
-- Tracks user login sessions for analytics and security monitoring
-- Note: logout_time column was removed as sessions are tracked by login only
CREATE TABLE user_sessions (
    id INT AUTO_INCREMENT PRIMARY KEY,                 -- Unique session identifier
    user_email VARCHAR(255) NOT NULL,                  -- Foreign key to users table
    login_time DATETIME NOT NULL,                      -- Timestamp when user logged in
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,  -- Cascade delete on user removal
    INDEX idx_user_email (user_email),                 -- Index for efficient user-based queries
    INDEX idx_login_time (login_time)                  -- Index for time-based session queries
);

-- ====================================================================
-- TOOL_USAGE TABLE
-- ====================================================================
-- General table for tracking usage of all AI tools in the application
-- Provides analytics on tool popularity and user engagement
CREATE TABLE IF NOT EXISTS tool_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,                 -- Unique usage record identifier
    user_email VARCHAR(255) NOT NULL,                  -- User who used the tool
    tool_name VARCHAR(50) NOT NULL,                    -- Name of the tool used (spam_text, deepfake_image, etc.)
    usage_time DATETIME NOT NULL,                      -- Timestamp when tool was used
    confidence_score FLOAT NOT NULL DEFAULT 0.0,       -- AI confidence score from the analysis
    result VARCHAR(50),                                -- Result of the analysis (spam/ham, real/deepfake, etc.)
    processing_time INT,                               -- Time taken to process the request (in milliseconds)
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,  -- Cascade delete on user removal
    INDEX idx_user_email (user_email),                 -- Index for user-based analytics
    INDEX idx_tool_name (tool_name),                   -- Index for tool-specific analytics
    INDEX idx_usage_time (usage_time),                 -- Index for time-based usage reports
    INDEX idx_tool_usage_composite (user_email, tool_name, usage_time)  -- Composite index for detailed analytics
);

-- ====================================================================
-- DEEPFAKE_IMAGE_RESULTS TABLE
-- ====================================================================
-- Stores detailed results from deepfake image detection analysis
-- Includes metadata about the image file and detection parameters
CREATE TABLE IF NOT EXISTS deepfake_image_results (
    id INT AUTO_INCREMENT PRIMARY KEY,                 -- Unique result record identifier
    user_email VARCHAR(255) NOT NULL,                  -- User who performed the analysis
    result VARCHAR(50) NOT NULL,                       -- Detection result (Real/Deepfake or AI Generated)
    confidence FLOAT NOT NULL,                         -- Confidence score from the AI model
    analysis_time DATETIME NOT NULL,                   -- Timestamp when analysis was performed
    image_path VARCHAR(255),                           -- Path to the analyzed image file
    model_used VARCHAR(50),                            -- AI model used for detection (e.g., resnet_inception)
    processing_time INT,                               -- Processing time in milliseconds
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,  -- Cascade delete on user removal
    INDEX idx_user_email (user_email),                 -- Index for user-specific results
    INDEX idx_analysis_time (analysis_time),           -- Index for time-based result queries
    INDEX idx_result (result)                          -- Index for result-based filtering
);

-- ====================================================================
-- DEEPFAKE_VIDEO_RESULTS TABLE
-- ====================================================================
-- Stores detailed results from deepfake video detection analysis
-- Similar structure to image results but without image_path (videos are processed differently)
CREATE TABLE IF NOT EXISTS deepfake_video_results (
    id INT AUTO_INCREMENT PRIMARY KEY,                 -- Unique result record identifier
    user_email VARCHAR(255) NOT NULL,                  -- User who performed the analysis
    result VARCHAR(50) NOT NULL,                       -- Detection result (Real/Deepfake or AI Generated)
    confidence FLOAT NOT NULL,                         -- Confidence score from the AI model
    analysis_time DATETIME NOT NULL,                   -- Timestamp when analysis was performed
    processing_time INT,                               -- Processing time in milliseconds
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,  -- Cascade delete on user removal
    INDEX idx_user_email (user_email),                 -- Index for user-specific results
    INDEX idx_analysis_time (analysis_time),           -- Index for time-based result queries
    INDEX idx_result (result)                          -- Index for result-based filtering
);

-- ====================================================================
-- SPAM_TEXT_RESULTS TABLE
-- ====================================================================
-- Stores detailed results from spam text detection analysis
-- Includes the actual text content that was analyzed
CREATE TABLE IF NOT EXISTS spam_text_results (
    id INT AUTO_INCREMENT PRIMARY KEY,                 -- Unique result record identifier
    user_email VARCHAR(255) NOT NULL,                  -- User who performed the analysis
    result VARCHAR(50) NOT NULL,                       -- Detection result (Spam mail/Ham mail)
    confidence FLOAT NOT NULL,                         -- Confidence score from the AI model
    analysis_time DATETIME NOT NULL,                   -- Timestamp when analysis was performed
    text_content TEXT,                                 -- The actual text content that was analyzed
    processing_time INT,                               -- Processing time in milliseconds
    FOREIGN KEY (user_email) REFERENCES users(email) ON DELETE CASCADE,  -- Cascade delete on user removal
    INDEX idx_user_email (user_email),                 -- Index for user-specific results
    INDEX idx_analysis_time (analysis_time),           -- Index for time-based result queries
    INDEX idx_result (result),                         -- Index for result-based filtering
    FULLTEXT INDEX idx_text_content (text_content)     -- Full-text index for text search capabilities
);

-- ====================================================================
-- ADDITIONAL INDEXES FOR PERFORMANCE OPTIMIZATION
-- ====================================================================
-- These indexes improve query performance for common access patterns

