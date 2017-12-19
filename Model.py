from flask.ext.sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()

#database
ROLE_USER = 0
ROLE_UPLOADER = 1
ROLE_AD = 2

class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text)
	like_num = db.Column(db.Integer, default = 0)
	create_time = db.Column(db.DateTime, default=datetime.datetime.now)
	location = db.Column(db.Integer)

	comment_id = db.relationship('PostComment', backref='post')

	def __repr__(self):
		return '<Post %s>' % self.content


class PostComment(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	content = db.Column(db.Text)
	create_time = db.Column(db.DateTime, default=datetime.datetime.now)
	
	post_id = db.Column(db.Integer, db.ForeignKey('post.id'))

	def __repr__(self):
		return '<Comment %s>' % self.content


class User(db.Model):
    __tablename__ = 'user'
    __searchable__ = ['username']
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    password = db.Column(db.String(32))
    res_id = db.relationship('LResource', backref = 'uploader')
    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def getRole(self):
        return self.role

    def get_id(self):
        return unicode(self.id)

    def __repr__(self):
        return "<User u'{name}'>".format(name = self.username)

class StandardAndSpe(db.Model):
    __tablename__ = 'standard'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    desc = db.Column(db.String(254))
    resource = db.relationship('LResource', secondary='res_std')

    def __init__(self, name, desc):
        self.name = name 
        self.desc = desc

    def __repr__(self):
        return '<StandardAndSpe %r>' % self.name

class Tool(db.Model):
    __tablename__ = 'tool'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    desc = db.Column(db.String(254))
    resource = db.relationship('LResource', secondary='res_tool')

    def __init__(self, name, desc):
        self.name = name 
        self.desc = desc

    def __repr__(self):
        return '<Tool %r>' % self.name


class Organization(db.Model):
    __tablename__ = 'organization'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    desc = db.Column(db.String(254))
    resource = db.relationship('LResource', secondary='res_org')

    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

    def __repr__(self):
        return '<Organization %r>' % self.name

class KnowledgeElement(db.Model):
    __tablename__ = 'knowledge'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    inlogic = db.Column(db.Integer)
    outlogic = db.Column(db.Integer)
    desc = db.Column(db.String(254))
    resource = db.relationship('LResource', secondary='res_ke')

    def __init__(self, name, inlogic, outlogic, desc):
        self.name = name
        self.inlogic = inlogic
        self.outlogic = outlogic
        self.desc = desc

    def __repr__(self):
        return '<KnowledgeElement %r>' % self.name


class KELinker(db.Model):
    __tablename__ = 'kelinker'
    fromke_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), primary_key=True)
    toke_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), primary_key=True)
    name = db.Column(db.String(40), index=True, unique=True)   
    desc = db.Column(db.String(254))

    def __init__(self, name, fromKeID, toKeID, desc):
        self.name = name
        self.fromke_id = fromKeID
        self.toke_id = toKeID
        self.desc = desc

    def __repr__(self):
        return '<KELinker %r>' % self.name


class Course(db.Model):
    __tablename__ = 'course'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True, unique=True)
    desc = db.Column(db.String(254))
    res_id = db.relationship('LResource')

    def __init__(self, name, desc):
        self.name = name
        self.desc = desc

    def __repr__(self):
        return '<Course %r>' % self.name


class LResource(db.Model):
    __tablename__ = 'resource'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40), index=True)
    types = db.Column(db.Integer)
    format = db.Column(db.Integer)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    url = db.Column(db.String(254))
    author = db.Column(db.String(40))
    uploader_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    uptime = db.Column(db.DateTime, default=datetime.datetime.now)
    updatetime = db.Column(db.DateTime, onupdate=datetime.datetime.now)
    desc = db.Column(db.String(254))
    addr = db.Column(db.String(254))
    standard = db.relationship('StandardAndSpe', secondary='res_std')
    tool = db.relationship('Tool', secondary='res_tool')
    organization = db.relationship('Organization', secondary='res_org')
    knowledge = db.relationship('KnowledgeElement', secondary='res_ke')

    def __init__(self, name, types, format, course_id, url, author, uploader_id, desc, addr, updatetime):
        self.name = name
        self.types = types
        self.format = format
        self.course_id = course_id
        self.url = url
        self.author = author
        self.uploader_id = uploader_id
        self.desc = desc
        self.addr = addr
        self.updatetime = updatetime

    def __repr__(self):
        list = {'name':self.name, 'types':self.types,'format':self.format,'course_id':self.course_id}
        # return "<User u'{name}'>".format(name = self.name)
        return "{'name': %r, 'types':%r, 'format':%r, 'id':%r}" % (self.name, self.types, self.format, self.course_id)
        # return '<Resource name : %r types : %r format: %r id: %r>' % (self.name, self.types, self.format, self.course_id)
        # return list


class Res_Std(db.Model):
    __tablename__ = 'res_std'
    res_id = db.Column(db.Integer, db.ForeignKey('resource.id'), primary_key=True)
    std_id = db.Column(db.Integer, db.ForeignKey('standard.id'), primary_key=True)

    def __init__(self, res, std):
        self.res_id = res
        self.std_id = std

    def __repr__(self):
        return '<Res_Std %r %r>' % (self.res_id, self.std_id)


class Res_Tool(db.Model):
    __tablename__ = 'res_tool'
    res_id = db.Column(db.Integer, db.ForeignKey('resource.id'), primary_key=True)
    tool_id = db.Column(db.Integer, db.ForeignKey('tool.id'), primary_key=True)

    def __init__(self, res, tool):
        self.res_id = res
        self.tool_id = tool

    def __repr__(self):
        return '<Res_Tool %r %r>' % (self.res_id, self.tool_id)


class Res_Org(db.Model):
    __tablename__ = 'res_org'
    res_id = db.Column(db.Integer, db.ForeignKey('resource.id'), primary_key=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organization.id'), primary_key=True)

    def __init__(self, res, org):
        self.res_id = res
        self.org_id = org

    def __repr__(self):
        return '<Res_Org %r %r>' % (self.res_id, self.org_id)


class Res_KE(db.Model):
    __tablename__ = 'res_ke'
    res_id = db.Column(db.Integer, db.ForeignKey('resource.id'), primary_key=True)
    ke_id = db.Column(db.Integer, db.ForeignKey('knowledge.id'), primary_key=True)
    degree = db.Column(db.Integer)
    desc = db.Column(db.Integer)
    def __init__(self, res, ke, degree, desc):
        self.res_id = res
        self.ke_id = ke
        self.degree = degree
        self.desc = desc

    def __repr__(self):
        return '<Res_KE %r %r %r>' % (self.res_id, self.ke_id, self.desc)

# class Comment(db.Model):
#     __tablename__ = 'comment'
#     id = db.Column(db.Integer, primary_key=True)
#     res_id = db.Column(db.Integer, db.ForeignKey('resource.id'))
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     datetime = db.Column(db.DateTime, default=db.func.now())

#     def __init__(self, res_id, user_id, datetime):
#         self.res_id = res_id
#         self.user_id = user_id
#         self.datetime = datetime

#     def __repr__(self):
#         return '<Comment %r %r %r>' % (self.res_id, self.user_id, self.datetime)

# class Notice(db.Model):
#     __tablename__ = 'notice'
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
#     datetime = db.Column(db.DateTime, default=db.func.now())

#     def __init__(self, user_id, datetime):
#         self.user_id = user_id
#         self.datetime = datetime

#     def __repr__(self):
#         return '<Comment %r %r>' % (self.user_id, self.datetime)