import psycopg2

# Функция, создающая структуру БД (таблицы)
def created_tables(conn, cur):
    cur.execute("""
                       CREATE TABLE IF NOT EXISTS users(
                           id SERIAL PRIMARY KEY,
                           name VARCHAR(40),
                           surname VARCHAR(40),
                           email VARCHAR(40)
                       );
                       """)
    cur.execute("""
                           CREATE TABLE IF NOT EXISTS phones(
                               id SERIAL PRIMARY KEY,
                               id_user INTEGER NOT NULL REFERENCES users(id),
                               number_phone VARCHAR(11) NOT NULL UNIQUE
                           );
                           """)
    conn.commit()
    print(f'Таблицы для БД созданы.')
# Функция, позволяющая добавить телефон для существующего клиента
def insert_phone_client(conn, cur, id_user, phone):
    for item in phone.split(","):
        cur.execute("""
                    INSERT INTO phones(id_user,number_phone) VALUES(%s,%s);
                    """, (id_user, item,))
    conn.commit()
    print(f'Телефон(ы) добавлены для пользователя с ID={id_user}')
# Функция, позволяющая добавить нового клиента
def insert_client(conn, cur, name, surname, email,phone=None):
    cur.execute("""
            INSERT INTO users(name,surname,email) VALUES(%s,%s,%s) RETURNING id;
            """,(name,surname,email,))
    if (len(phone)>0 and phone!=None):
        id = cur.fetchone()[0]
        insert_phone_client(conn, cur, id, phone)
    conn.commit()
    print(f'Клиент с ID={id} создан')
# Функция, позволяющая изменить данные о клиенте
def update_client(conn, cur, id):
    cur.execute("""
            UPDATE users SET name=%s, surname=%s, email=%s WHERE id=%s;
            """, (input('Введите имя: '), input('Введите фамилию: '), input('Введите email: '), id))
    conn.commit()
    print(f'Клиент с ID={id} изменен')
# Функция, позволяющая удалить телефон для существующего клиента
def drop_phones(conn, cur, id_user):
    cur.execute("""
           DELETE FROM phones WHERE id_user=%s;
           """, (id_user,))
    conn.commit()
    print(f'Телефон(ы) пользоватяля с ID={id_user} удалены')
# Функция, позволяющая удалить существующего клиента
def drop_user(conn, cur, id_user):
    cur.execute("""
               DELETE FROM users WHERE id=%s;
               """, (id_user,))
    conn.commit()
    print(f'Пользователь с ID={id_user} удален')
# Функция, позволяющая найти клиента по его данным (имени, фамилии, email-у или телефону)
def search_user(conn, cur, name=None, surname=None, email=None, phone=None):
    # cur.execute("SELECT * FROM users where name like '%%s%%' or surname like '%%s%%' or email like '%%s%%';"
    # ,(name, surname, email, ))
    d = list()
    query = "SELECT * FROM users"
    if phone!=None and len(phone)>0:
        query += f" join phones on users.id = phones.id_user where phones.number_phone='{phone}'"
    if (name!=None and len(name)>0) or (surname!=None and len(surname)>0) or (email!=None and len(email)>0):
        if phone!=None and len(phone)>0:
            query += ' and'
        else:
            query += ' where'
        if (name!=None and len(name)>0):
            query += f" name like '%{name}%'"
            d.append(name)
        if (name!=None and len(name)>0 and surname != None and len(surname) > 0):
            query += ' and'
        if (surname != None and len(surname) > 0):
            query += f" surname like '%{surname}%'"
            d.append(surname)
        if (((name != None and len(name) > 0) and (email != None and len(email) > 0)) or
            ((surname != None and len(surname) > 0) and (email != None and len(email) > 0))):
            query += ' and'
        if (email != None and len(email) > 0):
            query += f" email like '%{email}%'"
            d.append(email)
        query += ';'
        cur.execute(query)
    print(cur.fetchall())
    conn.commit()

if __name__ == '__main__':
    with psycopg2.connect(database="clients_db", user="postgres", password="...") as conn:
        with conn.cursor() as cur:
            created_tables(conn, cur)

            insert_client(conn, cur,input('Введите имя клиента: '), input('Введите фамилию клиента: '),
                          input('Введите email клиента: '), input('Введите телефон или телефоны через запятую (можете оставить пустым): '))

            insert_phone_client(conn, cur, input('Введите ID клиента: '), input('Введите телефон или телефоны через запятую: '))

            update_client(conn, cur, input('Введите ID клиента для редактирования: '))

            drop_phones(conn, cur, input('Введите ID клиента для удаления телефона(ов): '))

            drop_user(conn, cur, input('Введите ID клиента для удаления: '))

            search_user(conn, cur, input('Введите имя клиента или оставьте пустым: '),
                                   input('Введите фамилию клиента или оставьте пустым: '),
                                   input('Введите email клиента или оставьте пустым: '),
                                   input('Введите телефон или оставьте пустым: '))

    conn.close()