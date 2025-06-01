import socket
import threading
import mysql.connector
import getpass
from datetime import datetime
import re
import sys

HOST = '0.0.0.0'
PORT = 5000

stop_event = threading.Event()

def extract_schema_and_table(grant_query):
    match = re.search(r'GRANT\s+.*?\s+ON\s+(\w+)\.(\w+)', grant_query, re.IGNORECASE)
    if match:
        return match.group(1), match.group(2)
    else:
        raise ValueError("❌ Invalid GRANT query. Could not extract schema and table name.")

def extract_permissions(grant_query):
    match = re.search(r'GRANT\s+(.*?)\s+ON', grant_query, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    else:
        return "UNKNOWN"

def log_action(cursor, db, requester, permission_type, schema_name, table_name, grant_query, granted_permissions, status, admin_user):
    updated_at = datetime.now() if status != 'pending' else None
    cursor.execute("""
        INSERT INTO dev.permission_requests (
            requester, permission_type, schema_name, table_name,
            grant_query, granted_permissions, status, admin_user, updated_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        requester, permission_type, schema_name, table_name,
        grant_query, granted_permissions, status, admin_user, updated_at
    ))
    db.commit()

def handle_client(conn, addr, admin_user, admin_pass):
    try:
        data = conn.recv(8192).decode()
        requester, grant_query = data.split("||", 1)

        schema_name, table_name = extract_schema_and_table(grant_query)
        granted_permissions = extract_permissions(grant_query)
        permission_type = "GRANT"

        print(f"\n--- New Permission Request ---")
        print(f"From: {requester}")
        print(f"Schema: {schema_name}")
        print(f"Table: {table_name}")
        print(f"Permissions: {granted_permissions}")
        print(f"Query: {grant_query}")
        decision = input("Approve or Reject [A/R]: ").strip().upper()

        db = mysql.connector.connect(
            host="localhost",
            user=admin_user,
            password=admin_pass,
            database=schema_name
        )
        cursor = db.cursor()

        if decision == 'A':
            try:
                cursor.execute(grant_query)
                db.commit()
                conn.sendall(b"APPROVED")
                log_action(cursor, db, requester, permission_type, schema_name, table_name, grant_query, granted_permissions, 'approved', admin_user)
                print("✅ Query approved and executed.")
            except Exception as e:
                conn.sendall(f"ERROR: {str(e)}".encode())
                print(f"❌ Error executing query: {e}")
        else:
            conn.sendall(b"REJECTED")
            log_action(cursor, db, requester, permission_type, schema_name, table_name, grant_query, granted_permissions, 'rejected', admin_user)
            print("❌ Query rejected.")

        db.close()
    except Exception as e:
        print(f"Error handling client {addr}: {e}")
    finally:
        conn.close()

def main():
    admin_user = input("Enter MySQL admin username: ")
    admin_pass = getpass.getpass("Enter MySQL password: ")

    print(f"🔐 Admin server running on {HOST}:{PORT}... (Press Ctrl+C to stop)")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(1.0)  # Allow checking for stop_event regularly

        try:
            while not stop_event.is_set():
                try:
                    conn, addr = s.accept()
                    threading.Thread(target=handle_client, args=(conn, addr, admin_user, admin_pass)).start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("\n🛑 Admin server shutting down...")
            stop_event.set()
            sys.exit(0)

if __name__ == "__main__":
    main()
