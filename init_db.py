import sqlite3

connection = sqlite3.connect('database.db')


with open('schema.sql') as f:
    connection.executescript(f.read())

cur = connection.cursor()

# cur.execute("INSERT INTO posts (title, content) VALUES (?, ?)",
#             ('First Post', 'Content for the first post')
#             )

cur.execute("INSERT INTO posts (title, email, ticket, ceilings, floors) VALUES (?, ?, ?, ?, ?)",
            ('Michael', 'michael1234@yahoo.com', 'NDAQ', 200, 100)
            )

connection.commit()
connection.close()