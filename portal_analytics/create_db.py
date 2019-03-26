import psycopg2

conn = psycopg2.connect("dbname='michael' user='michael' host='127.0.0.1'")
cur = conn.cursor()

cur.execute('''create table add_layers 
(id serial,
       layername VARCHAR(256),
       extent geometry,
       qualifier VARCHAR(2048));

''')
conn.commit()