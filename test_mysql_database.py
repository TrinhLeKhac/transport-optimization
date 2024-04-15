import mysql.connector

db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='superai@12345',
    port='3306',
    database='superai',
)

cursor = db.cursor()

# cursor.execute("CREATE TABLE Person (name varchar(50), age smallint, personID int PRIMARY KEY AUTO_INCREMENT)")
# cursor.execute("INSERT INTO Person (name, age) VALUES ('trinhlk2', 11)")
cursor.execute("SELECT * FROM user")

persons = cursor.fetchall()

for person in persons:
    print(person)



