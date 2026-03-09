#!/usr/bin/env python3
"""
Speech Recognition Error Analytics Script
Run this to view error statistics from the database
"""

import sqlite3
import json
from datetime import datetime

def get_error_stats():
    """Get speech recognition error statistics"""
    conn = sqlite3.connect('language_learning.db')
    cursor = conn.cursor()

    # Get browser statistics
    cursor.execute("""
        SELECT browser, COUNT(*) as count
        FROM speech_error
        GROUP BY browser
        ORDER BY count DESC
    """)
    browser_stats = cursor.fetchall()

    # Get error type statistics
    cursor.execute("""
        SELECT error_type, COUNT(*) as count
        FROM speech_error
        GROUP BY error_type
        ORDER BY count DESC
    """)
    error_type_stats = cursor.fetchall()

    # Get language statistics
    cursor.execute("""
        SELECT language, COUNT(*) as count
        FROM speech_error
        WHERE language IS NOT NULL
        GROUP BY language
        ORDER BY count DESC
    """)
    language_stats = cursor.fetchall()

    # Get recent errors
    cursor.execute("""
        SELECT browser, error_type, error_message, language, timestamp
        FROM speech_error
        ORDER BY timestamp DESC
        LIMIT 20
    """)
    recent_errors = cursor.fetchall()

    conn.close()

    return {
        'browser_stats': browser_stats,
        'error_type_stats': error_type_stats,
        'language_stats': language_stats,
        'recent_errors': recent_errors
    }

def print_stats():
    """Print formatted statistics"""
    stats = get_error_stats()

    print("🎯 SPEECH RECOGNITION ERROR ANALYTICS")
    print("=" * 50)

    print("\n📊 Errors by Browser:")
    for browser, count in stats['browser_stats']:
        print(f"  {browser}: {count} errors")

    print("\n🚨 Errors by Type:")
    for error_type, count in stats['error_type_stats']:
        print(f"  {error_type}: {count} errors")

    print("\n🌍 Errors by Language:")
    for language, count in stats['language_stats']:
        print(f"  {language}: {count} errors")

    print("\n🕐 Recent Errors (Last 20):")
    for error in stats['recent_errors']:
        browser, error_type, message, language, timestamp = error
        lang_str = f" ({language})" if language else ""
        print(f"  {browser}{lang_str}: {error_type} - {message[:50]}...")

    total_errors = sum(count for _, count in stats['browser_stats'])
    print(f"\n📈 Total Errors Logged: {total_errors}")

if __name__ == "__main__":
    print_stats()