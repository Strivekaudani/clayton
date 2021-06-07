
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine("sqlite:///data.sqlite3")
db = scoped_session(sessionmaker(bind=engine))

# creating tables
## reading sql file
# f = open("tables.sql", 'r');
# contents = f.read();

# statements = contents.split(';');

# ## executing sql statements
# for statement in statements:

# 	statement = statement.strip();

# 	if (statement == ''):
# 		continue

# 	statement = statement.replace('\r\n', ' ')
# 	statement = statement.replace('\n\r', ' ')
# 	statement = statement.replace('\n', ' ')
# 	statement = statement.replace('\r', ' ')

# 	try:
# 		db.execute(statement);
# 		db.commit()
# 		# print(statement)
# 	except Exception as e:
# 		# print(statement);
# 		# print (str(e))
# 		pass

# # initializing datasets

# try:
# 	sql = 'INSERT INTO users (name, surname, email, password, is_admin, funds) VALUES (:name, :surname, :email, :password, :is_admin, :funds)'
# 	data = {
# 		"name": "CLAYTON",
# 		"surname": "SIBANDA",
# 		"email": "claytonsibanda@gmail.com",
# 		"password": "admin",
# 		"is_admin": 1,
# 		"funds": 0
# 	}

# 	db.execute(sql, data)
# 	db.commit();
# except Exception:
# 	pass