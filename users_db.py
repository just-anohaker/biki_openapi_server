import sqlite3,uuid

conn = sqlite3.connect('biki.db', check_same_thread=False)

db = conn.cursor()

def init_db():
    db.execute(''' create table if not exists users (id text primary key, 
                                    name text not null,
                                    groupName text not null, 
                                    httpkey text not null,
                                    httpsecret text not null,
                                    state integer not null);
    ''')
    conn.commit()

def query_db(query, args=(), one=False):
    cur = db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
            for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv

def users_all():
    sql = 'select * from users;'
    return query_db(sql)

def users_remove(para):
    sql = '''update users set state=? where id=?;'''
    db.execute(sql,(1,para))
    conn.commit()
    sql = 'select * from users where  id=:userId ;'
    return  query_db(sql, (para,) )

def users_add(para):
    print(para)
    sql = '''insert into users (id, groupName, name, httpkey, httpsecret,  state) values(?,?,
     ?, ?, ?, ?);'''
    para['id'] = str(uuid.uuid4())
    para['state'] = 0
    db.execute(sql,(para['id'],para['groupName'],para['name'],para['httpkey'],para['httpsecret'],para['state']))
    conn.commit()
    sql = 'select * from users where  id=:userId ;'
    return  query_db(sql, (para['id'],), one=True)

def users_update(para):
    sql = '''update users set
            groupName=:groupName, name=:name, httpKey=:httpkey, httpSecret=:httpsecret
            where id=:userId ;'''
    db.execute(sql,para)
    conn.commit() 
    sql = 'select * from users where  id=:userId ;'
    return query_db(sql,para)

def users_all_invalid():
    sql = 'select * from users where state = 1;'
    return query_db(sql)

def users_all_valid():
    sql = 'select * from users where state = 0;'
    return query_db(sql)

init_db()
# users_insert(('11111','test_group','test_name','test_key','test_sect','test_p',0))

#users_remove('11111')

#users_update({'groupName':'test2','name':'ok','httpKey':'hh','httpSecret':'sg','userId':'11111','state':1})
#print(users_all_valid())