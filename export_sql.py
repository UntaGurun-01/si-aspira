import pymysql

conn = pymysql.connect(host='127.0.0.1', user='root', password='', port=3306, database='si_pengaduan')
cur = conn.cursor()

sql_lines = [
    '-- =========================================================',
    '-- SI PENGADU - Database Dump for phpMyAdmin / MySQL',
    '-- Sistem Pengaduan Mahasiswa Prodi Teknik Informatika',
    '-- Universitas Pahlawan Tuanku Tambusai',
    '-- =========================================================',
    '',
    'SET FOREIGN_KEY_CHECKS = 0;',
    'CREATE DATABASE IF NOT EXISTS `si_pengaduan` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;',
    'USE `si_pengaduan`;',
    ''
]

cur.execute('SHOW TABLES;')
tables = [t[0] for t in cur.fetchall()]

for table in tables:
    sql_lines.append(f'-- Table structure for `{table}`')
    sql_lines.append(f'DROP TABLE IF EXISTS `{table}`;')
    cur.execute(f'SHOW CREATE TABLE `{table}`;')
    create_stmt = cur.fetchone()[1]
    sql_lines.append(create_stmt + ';')
    sql_lines.append('')

    cur.execute(f'SELECT * FROM `{table}`;')
    rows = cur.fetchall()
    if rows:
        cur.execute(f'SHOW COLUMNS FROM `{table}`;')
        cols = [f'`{c[0]}`' for c in cur.fetchall()]
        col_str = ', '.join(cols)
        sql_lines.append(f'-- Dumping data for `{table}`')
        for r in rows:
            vals = []
            for v in r:
                if v is None:
                    vals.append('NULL')
                elif isinstance(v, (int, float)):
                    vals.append(str(v))
                else:
                    escaped = str(v).replace('\\', '\\\\').replace("'", "\\'")
                    vals.append(f"'{escaped}'")
            val_str = ', '.join(vals)
            sql_lines.append(f'INSERT INTO `{table}` ({col_str}) VALUES ({val_str});')
        sql_lines.append('')

sql_lines.append('SET FOREIGN_KEY_CHECKS = 1;')

with open('si_pengaduan.sql', 'w', encoding='utf-8') as f:
    f.write('\n'.join(sql_lines))

print('si_pengaduan.sql generated successfully!')
conn.close()
