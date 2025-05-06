import mysql.connector
from mysql.connector import errorcode

config = {
    'user': 'root',
    'password': '3583',
    'host': '127.0.0.1',
    'raise_on_warnings': True
}

DB_NAME = 'lib_management'

TABLES = {}

TABLES['activitylogs'] = (
    "CREATE TABLE activitylogs ("
    "  log_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  library_id INT NOT NULL,"
    "  staff_id INT,"
    "  member_id INT,"
    "  book_id INT,"
    "  activity_type_id INT NOT NULL,"
    "  description TEXT NOT NULL,"
    "  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,"
    "  FOREIGN KEY (library_id) REFERENCES library(library_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (staff_id) REFERENCES librarystaff(staff_id) ON DELETE SET NULL,"
    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE SET NULL,"
    "  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE SET NULL,"
    "  FOREIGN KEY (activity_type_id) REFERENCES activitytypes(activity_type_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['activitytypes'] = (
    "CREATE TABLE activitytypes ("
    "  activity_type_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  activity_type ENUM('Borrow', 'Return', 'Fine Payment', 'Reservation', 'Membership Renewal') NOT NULL"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['admin'] = (
    "CREATE TABLE admin ("
    "  admin_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  library_id INT NOT NULL,"
    "  name VARCHAR(255) NOT NULL,"
    "  email VARCHAR(255) NOT NULL UNIQUE,"
    "  phone VARCHAR(20) NOT NULL,"
    "  password VARCHAR(255) NOT NULL,"
    "  role_id INT NOT NULL,"
    "  FOREIGN KEY (library_id) REFERENCES library(library_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['book_authors'] = (
    "CREATE TABLE book_authors ("
    "  book_id INT NOT NULL,"
    "  author VARCHAR(255) NOT NULL,"
    "  PRIMARY KEY (book_id, author),"
    "  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['books'] = (
    "CREATE TABLE books ("
    "  book_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  library_id INT NOT NULL,"
    "  title VARCHAR(255) NOT NULL,"
    "  genre VARCHAR(100) NOT NULL,"
    "  isbn VARCHAR(20) NOT NULL UNIQUE,"
    "  published_year INT NOT NULL,"
    "  copies_available INT NOT NULL CHECK (copies_available >= 0),"
    "  FOREIGN KEY (library_id) REFERENCES library(library_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['borrowedbooks'] = (
    "CREATE TABLE borrowedbooks ("
    "  transaction_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  member_id INT NOT NULL,"
    "  book_id INT NOT NULL,"
    "  borrow_date DATE NOT NULL DEFAULT (CURDATE()),"
    "  due_date DATE NOT NULL,"
    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['fine_amounts'] = (
    "CREATE TABLE fine_amounts ("
    "  fine_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  amount DECIMAL(10,2) NOT NULL"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['fines'] = (
    "CREATE TABLE fines ("
    "  fine_id INT NOT NULL,"
    "  member_id INT NOT NULL,"
    "  status ENUM('Paid', 'Unpaid') NOT NULL DEFAULT 'Unpaid',"
    "  payment_date DATE DEFAULT NULL,"
    "  PRIMARY KEY (fine_id, member_id),"
    "  FOREIGN KEY (fine_id) REFERENCES fine_amounts(fine_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['isborrowed'] = (
    "CREATE TABLE isborrowed ("
    "  transaction_id INT NOT NULL PRIMARY KEY,"
    "  is_borrowed TINYINT(1) NOT NULL DEFAULT 1,"
    "  FOREIGN KEY (transaction_id) REFERENCES borrowedbooks(transaction_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['issued_books'] = (
    "CREATE TABLE issued_books ("
    "  issue_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  book_id INT NOT NULL,"
    "  member_id INT NOT NULL,"
    "  issue_date DATE NOT NULL,"
    "  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['library'] = (
    "CREATE TABLE library ("
    "  library_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  library_name VARCHAR(255) NOT NULL,"
    "  library_address TEXT NOT NULL,"
    "  library_contact VARCHAR(20) NOT NULL,"
    "  library_email VARCHAR(255) NOT NULL UNIQUE,"
    "  established_year INT NOT NULL"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['librarystaff'] = (
    "CREATE TABLE librarystaff ("
    "  staff_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  library_id INT NOT NULL,"
    "  name VARCHAR(255) NOT NULL,"
    "  email VARCHAR(255) NOT NULL UNIQUE,"
    "  phone VARCHAR(20) NOT NULL,"
    "  role ENUM('Librarian', 'Assistant', 'Manager') NOT NULL,"
    "  hire_date DATE NOT NULL,"
    "  salary DECIMAL(10,2) NOT NULL,"
    "  admin_id INT,"
    "  FOREIGN KEY (library_id) REFERENCES library(library_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['logs'] = (
    "CREATE TABLE logs ("
    "  log_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  log_message TEXT NOT NULL,"
    "  log_date DATETIME NOT NULL"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['members'] = (
    "CREATE TABLE members ("
    "  member_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  library_id INT NOT NULL,"
    "  name VARCHAR(255) NOT NULL,"
    "  email VARCHAR(255) NOT NULL UNIQUE,"
    "  phone VARCHAR(20) NOT NULL,"
    "  membership_type ENUM('Regular', 'Premium') NOT NULL,"
    "  registration_date DATE NOT NULL DEFAULT (CURDATE()),"
    "  FOREIGN KEY (library_id) REFERENCES library(library_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['reservations'] = (
    "CREATE TABLE reservations ("
    "  reservation_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  member_id INT NOT NULL,"
    "  book_id INT NOT NULL,"
    "  reservation_date DATE NOT NULL DEFAULT (CURDATE()),"
    "  status ENUM('Pending', 'Completed', 'Canceled') NOT NULL DEFAULT 'Pending',"
    "  FOREIGN KEY (member_id) REFERENCES members(member_id) ON DELETE CASCADE,"
    "  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE CASCADE"
    ") ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['roles'] = (
    "CREATE TABLE roles ("
    "  role_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  role ENUM('Super Admin', 'Librarian', 'Assistant') NOT NULL"
    ") ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

TABLES['staffs'] = (
    "CREATE TABLE staffs ("
    "  staff_id INT AUTO_INCREMENT PRIMARY KEY,"
    "  name VARCHAR(255) NOT NULL,"
    "  role VARCHAR(255) NOT NULL,"
    "  email VARCHAR(255) NOT NULL"
    ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci"
)

def create_database(cursor):
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS {DB_NAME} DEFAULT CHARACTER SET 'utf8mb4' COLLATE 'utf8mb4_0900_ai_ci'")
        print(f"Database {DB_NAME} created or already exists.")
    except mysql.connector.Error as err:
        print(f"Failed creating database: {err}")
        exit(1)

def create_tables(cursor):
    for table_name in TABLES:
        table_description = TABLES[table_name]
        try:
            print(f"Creating table {table_name}... ", end='')
            cursor.execute(table_description)
            print("OK")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
                print("already exists.")
            else:
                print(err.msg)

def main():
    try:
        cnx = mysql.connector.connect(**config)
        cursor = cnx.cursor()
        create_database(cursor)
        cnx.database = DB_NAME
        create_tables(cursor)
        cursor.close()
        cnx.close()
        print("All tables created successfully.")
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

if __name__ == '__main__':
    main()
