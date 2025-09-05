#!/usr/bin/env python3
"""
Database Verification Script for Spam Watch Project
This script verifies the database structure and tests data storage
"""

import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

def verify_database():
    """Verify database structure and connectivity"""
    try:
        # Database connection parameters
        connection = mysql.connector.connect(
            host='localhost',
            user='spamwatchuser',
            password='StrongPassword123!',
            database='spamwatchdb'
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            print("=== DATABASE VERIFICATION REPORT ===")
            print(f"Connected to MySQL Server version: {connection.get_server_info()}")
            print(f"Database: {connection.database}")
            print()
            
            # Check all tables
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            print("Available Tables:")
            for table in tables:
                print(f"  - {table[0]}")
            print()
            
            # Check table structures
            for table in tables:
                table_name = table[0]
                print(f"=== {table_name.upper()} TABLE STRUCTURE ===")
                cursor.execute(f"DESCRIBE {table_name}")
                columns = cursor.fetchall()
                for column in columns:
                    print(f"  {column[0]}: {column[1]} {'NULL' if column[2] == 'YES' else 'NOT NULL'} {column[3]}")
                print()
                
                # Check data count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                print(f"  Records: {count}")
                
                # Show sample data if exists
                if count > 0:
                    print("  Sample Data:")
                    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
                    rows = cursor.fetchall()
                    for row in rows:
                        print(f"    {row}")
                print()
            
            # Check foreign key relationships
            print("=== FOREIGN KEY RELATIONSHIPS ===")
            cursor.execute("""
                SELECT TABLE_NAME, COLUMN_NAME, CONSTRAINT_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME
                FROM INFORMATION_SCHEMA.KEY_COLUMN_USAGE
                WHERE TABLE_SCHEMA = 'spamwatchdb' AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            fk_relationships = cursor.fetchall()
            for rel in fk_relationships:
                print(f"  {rel[0]}.{rel[1]} -> {rel[3]}.{rel[4]}")
            
            cursor.close()
            connection.close()
            
    except Error as e:
        print(f"Database Error: {e}")
        return False
    
    return True

def create_complete_schema():
    """Create complete database schema including missing users table"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='spamwatchuser',
            password='StrongPassword123!'
        )
        
        cursor = connection.cursor()
        
        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS spamwatchdb")
        cursor.execute("USE spamwatchdb")
        
        # Create users table (missing from original schema)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                email VARCHAR(255) PRIMARY KEY,
                password_hash VARCHAR(255) NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create all other tables
        tables_sql = [
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                login_time DATETIME NOT NULL,
                logout_time DATETIME,
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS tool_usage (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                tool_name VARCHAR(50) NOT NULL,
                usage_time DATETIME NOT NULL,
                confidence_score FLOAT,
                classification VARCHAR(50),
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS deepfake_image_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                result VARCHAR(50) NOT NULL,
                confidence FLOAT NOT NULL,
                analysis_time DATETIME NOT NULL,
                image_path VARCHAR(255),
                model_used VARCHAR(50),
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS deepfake_video_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                result VARCHAR(50) NOT NULL,
                confidence FLOAT NOT NULL,
                analysis_time DATETIME NOT NULL,
                video_path VARCHAR(255),
                model_used VARCHAR(50),
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS spam_text_results (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                result VARCHAR(50) NOT NULL,
                confidence FLOAT NOT NULL,
                analysis_time DATETIME NOT NULL,
                text_content TEXT,
                FOREIGN KEY (user_email) REFERENCES users(email)
            )
            """
        ]
        
        for sql in tables_sql:
            cursor.execute(sql)
        
        connection.commit()
        print("✅ Complete database schema created successfully!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Schema Creation Error: {e}")
        return False
    
    return True

def test_data_storage():
    """Test data storage with sample data"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='spamwatchuser',
            password='StrongPassword123!',
            database='spamwatchdb'
        )
        
        cursor = connection.cursor()
        
        # Insert test user
        from werkzeug.security import generate_password_hash
        test_email = "test@example.com"
        test_password = generate_password_hash("test123")
        
        cursor.execute("""
            INSERT IGNORE INTO users (email, password_hash) 
            VALUES (%s, %s)
        """, (test_email, test_password))
        
        # Insert test data
        cursor.execute("""
            INSERT INTO deepfake_image_results 
            (user_email, result, confidence, analysis_time, image_path, model_used)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, (test_email, "Real", 95.5, "test_image.jpg", "resnet_inception"))
        
        cursor.execute("""
            INSERT INTO deepfake_video_results 
            (user_email, result, confidence, analysis_time, video_path, model_used)
            VALUES (%s, %s, %s, NOW(), %s, %s)
        """, (test_email, "Fake", 87.3, "test_video.mp4", "resnet_inception"))
        
        cursor.execute("""
            INSERT INTO spam_text_results 
            (user_email, result, confidence, analysis_time, text_content)
            VALUES (%s, %s, %s, NOW(), %s)
        """, (test_email, "Spam", 92.1, "This is a test spam message"))
        
        connection.commit()
        print("✅ Test data inserted successfully!")
        
        cursor.close()
        connection.close()
        
    except Error as e:
        print(f"Test Data Error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("Starting Database Verification...")
    print()
    
    # Create complete schema
    print("1. Creating complete database schema...")
    create_complete_schema()
    print()
    
    # Verify database
    print("2. Verifying database structure...")
    verify_database()
    print()
    
    # Test data storage
    print("3. Testing data storage...")
    test_data_storage()
    print()
    
    print("=== VERIFICATION COMPLETE ===")
