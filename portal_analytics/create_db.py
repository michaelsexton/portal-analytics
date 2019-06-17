import psycopg2

def create_tables():
    conn = psycopg2.connect("dbname='postgres' user='postgres' host='127.0.0.1'")
    cur = conn.cursor()

    cur.execute('''create table add_layers 
        ( id serial,
          layername VARCHAR(256),
          extent geometry,
          qualifier VARCHAR(2048),
          events integer);
      ''')
    conn.commit()