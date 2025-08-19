#!/usr/bin/env python3
"""Verify database contents after successful orchestration."""

import sqlite3
import json

def verify_database():
    print("🔍 VERIFYING DATABASE CONTENTS")
    print("="*50)
    
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    
    # Get all table names
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"📊 Tables: {tables}")
    
    # Check agents table
    print("\n1️⃣ AGENTS TABLE:")
    cursor.execute("SELECT * FROM agents")
    agents = cursor.fetchall()
    print(f"   Count: {len(agents)}")
    for agent in agents:
        print(f"   - ID: {agent[0]}")
        print(f"     Name: {agent[1]}")
        print(f"     Type: {agent[2]}")
        print(f"     Status: {agent[3]}")
        print(f"     Capabilities: {agent[4]}")
        print(f"     Metadata: {agent[5]}")
    
    # Check sessions table
    print("\n2️⃣ SESSIONS TABLE:")
    cursor.execute("SELECT * FROM sessions")
    sessions = cursor.fetchall()
    print(f"   Count: {len(sessions)}")
    for session in sessions:
        print(f"   - Session ID: {session[0]}")
        print(f"     Agent ID: {session[1]}")
        print(f"     Task: {session[2]}")
        print(f"     Created: {session[3]}")
    
    # Check tasks table
    print("\n3️⃣ TASKS TABLE:")
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    print(f"   Count: {len(tasks)}")
    for task in tasks:
        print(f"   - Task ID: {task[0]}")
        print(f"     Description: {task[1]}")
        print(f"     Status: {task[2]}")
    
    # Check messages table
    print("\n4️⃣ MESSAGES TABLE:")
    cursor.execute("SELECT * FROM messages")
    messages = cursor.fetchall()
    print(f"   Count: {len(messages)}")
    for msg in messages[:3]:  # Show first 3
        print(f"   - From: {msg[1]} To: {msg[2]}")
        print(f"     Content: {msg[3][:60]}...")
    
    # Check checkpoints table
    print("\n5️⃣ CHECKPOINTS TABLE:")
    cursor.execute("SELECT * FROM checkpoints")
    checkpoints = cursor.fetchall()
    print(f"   Count: {len(checkpoints)}")
    for cp in checkpoints:
        print(f"   - ID: {cp[0]}")
        print(f"     Name: {cp[1]}")
        try:
            data = json.loads(cp[2])
            print(f"     Type: {data.get('type', 'unknown')}")
            print(f"     Orchestration ID: {data.get('orchestration_id', 'N/A')[:8]}...")
        except:
            print(f"     Data: {cp[2][:60]}...")
        print(f"     Created: {cp[3]}")
    
    conn.close()
    
    # Summary
    total_records = len(agents) + len(sessions) + len(tasks) + len(messages) + len(checkpoints)
    
    print(f"\n" + "="*50)
    print(f"📊 TOTAL RECORDS: {total_records}")
    print(f"   • Agents: {len(agents)}")
    print(f"   • Sessions: {len(sessions)}")  
    print(f"   • Tasks: {len(tasks)}")
    print(f"   • Messages: {len(messages)}")
    print(f"   • Checkpoints: {len(checkpoints)}")
    
    if total_records > 0:
        print("✅ DATABASE INTEGRATION FULLY WORKING!")
        return True
    else:
        print("❌ NO DATA IN DATABASE!")
        return False

if __name__ == "__main__":
    verify_database()