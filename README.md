# 🛡️ MySQL GRANT Permission Approval System

A secure, admin-controlled GRANT permission approval system built with **Python**, **Sockets**, and **MySQL**. This project enables database administrators (DBAs) to manage permission requests efficiently by allowing users to submit access requests via a client interface, which the admin can then approve or reject in real-time.

---

## 📌 About the Project

Directly granting database permissions can pose significant security risks. This tool provides a controlled, auditable process to handle permission escalation requests:

- Users submit `GRANT` queries for approval.
- Admins receive real-time notifications and manually approve or reject requests.
- All actions are logged in a centralized `permission_requests` table.
- Admins maintain full control and visibility before permissions are granted.
- Supports multiple client requests with graceful shutdown using `Ctrl+C`.

---

## 🧩 Technologies Used

- Python 3
- MySQL Database
- `mysql-connector-python` for database connectivity
- Socket programming for client-server communication
- Threading to handle concurrent connections

---

## ⚙️ Setup Instructions

### 1. ✅ Create MySQL Table

Execute the following SQL script in your `dev` database to create the necessary table:

```sql
CREATE TABLE database_name.table_name (
    id INT AUTO_INCREMENT PRIMARY KEY,
    requester VARCHAR(100),
    permission_type VARCHAR(100),
    schema_name VARCHAR(100),
    table_name VARCHAR(100),
    grant_query TEXT,
    granted_permissions TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    admin_user VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL
);
