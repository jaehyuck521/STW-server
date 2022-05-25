from sqlalchemy import create_engine, text

db={
    'user':'root',
    'password':'password',
    'host':'stw-db2.cfds7yjqxmf6.ap-northeast-2.rds.amazonaws.com',
    'port': 3306,
    'database': 'worry'
}
DB_URL=f"mysql+mysqlconnector://{db['user']}:{db['password']}@{db['host']}:{db['port']}/{db['database']}?charset=utf8"
JWT_SECRET_KEY = 'SOME_SUPER_SECRET_KEY'
# db=create_engine(db_url, encoding='utf-8',max_overflow=0)
# params={'userid':'flysamsung'}
# rows=db.execute(text("select * from user where userid=:userid"),params).fetchall()
# for row in rows:
#     print(f"name: {row['name']}")