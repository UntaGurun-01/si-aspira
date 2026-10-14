import pymysql
from werkzeug.security import generate_password_hash

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='', database='si_pengaduan')
cursor = conn.cursor()

# Create admins table
create_sql = """
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    is_active TINYINT(1) DEFAULT 1,
    avatar VARCHAR(255) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME NULL
)
"""
cursor.execute(create_sql)
print("Tabel 'admins' berhasil dibuat!")

# Insert demo admin account (password: admin123)
pw = generate_password_hash('admin123')
insert_sql = """
INSERT IGNORE INTO admins (name, email, username, password_hash, role, is_active)
VALUES (%s, %s, %s, %s, %s, %s)
"""
cursor.execute(insert_sql, (
    'Administrator Utama',
    'admin@universitaspahlawan.ac.id',
    'admin',
    pw,
    'superadmin',
    1
))
conn.commit()
print("Akun demo admin berhasil dibuat!")
print("Username: admin")
print("Password: admin123")

cursor.close()
conn.close()
print("DONE!")
