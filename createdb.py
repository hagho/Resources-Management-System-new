# coding: utf-8

from app import db
db.create_all()

from app import *

for i in range(10):
	user = User('abc'+str(i), 'abc'+str(i), 'abc'+str(i))
	db.session.add(user)

db.session.commit()

for i in range(10):
	s = 'standard' + str(i)
	standard = StandardAndSpe(s, s)
	db.session.add(standard)

db.session.commit()

for i in range(10):
	s = 'Knowledge' + str(i)
	know = KnowledgeElement(s, i, i, s)
	db.session.add(know)

db.session.commit()

for i in range(10):
	s = 'Tool' + str(i)
	tool = Tool(s, s)
	db.session.add(tool)

db.session.commit()

for i in range(10):
	s = 'Organization' + str(i)
	org = Organization(s, s)
	db.session.add(org)

db.session.commit()


course = Course('SOA', 'SOA description')
db.session.add(course)
course = Course('SOC', 'SOC description')
db.session.add(course)
db.session.commit()



for i in range(10):
	re = LResource('abc'+str(i), i%2, i%2, i%2, 'abc'+str(i), 'abc'+str(i), i%4, 'abc'+str(i), 'abc'+str(i))
	db.session.add(re)
db.session.commit()

for i in range(10):
	re = LResource.query.filter_by(id = i+1).first()
	re.format = re.format+1
	db.session.commit()

# userall =  User.query.filter_by(role = 1).group_by(User.id).all()
# for u in userall:
# 	print u.id
