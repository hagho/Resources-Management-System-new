# coding: utf-8
from flask.ext.wtf import Form
from wtforms import widgets, StringField, SubmitField, BooleanField, TextField, PasswordField, TextAreaField, HiddenField, SelectField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Required, EqualTo, EqualTo, URL, InputRequired
from flask.ext.wtf.file import FileField, FileAllowed, FileRequired
from Model import *
from app import db



class UserForm(Form):
	username = TextField('用户名',[DataRequired(message="用户名不能为空")], description = '您的用户名')
	email = TextField('邮箱', [DataRequired(message="邮箱不能为空"), Email(message="无效的邮箱")],
                      description='您常用的邮箱')
	password = PasswordField('密码',[DataRequired(message="密码不能为空")], description = '您的密码')
	confirm = PasswordField('重复输入密码', [
          Required(),
          EqualTo('password', message='请重复输入一次密码')
          ])
	submit = SubmitField('注册')

class SigninForm(Form):
	username = StringField('用户名',[DataRequired(message="用户名不能为空")], description = '')
	password = PasswordField('密码',[DataRequired(message="密码不能为空")], description = '')
	remember_me = BooleanField('Remember me', default = False)
	submit = SubmitField('登录')

class SearchForm(Form):
	title = StringField('标题',[DataRequired(message = "标题不能为空")], description = '您想搜索的标题')
	submit = SubmitField('提交')

class UploadForm(Form):
	file = FileField(u'资源上传', validators=[DataRequired('请上传后提交')])
	name = TextField(u'资源名称', [DataRequired(u'资源名称不能为空')])
	types = SelectField(u'类别', choices=[('1', u'教学计划'), ('2',u'教学大纲'), ('3',u'教学方案'), ('4',u'教材'), ('5', u'课件'), ('6', u'案例描述'), ('7', u'案例参考答案'), ('8', u'试验题目'), ('9', u'实验指导'), ('10', u'实验报告'), ('11', u'试卷'), ('12', u'试卷答案'), ('13', u'练习')])
	format = SelectField(u'格式', choices=[('1', u'文档'), ('2',u'视频'), ('3',u'音频')])
	course = SelectField(u'课程名称', choices=zip(list(zip(*(db.session.query(Course, Course.name).all()))[1]), list(zip(*(db.session.query(Course, Course.name).all()))[1])))

	url = TextField(u'资源地址', [DataRequired(u'地址不能为空'), URL(message="无效的地址")])
	author = TextField(u'作者',  [DataRequired(u'作者不能为空')])
	desc = TextAreaField(u'资源描述', [DataRequired(u'描述不能为空')])
	# standard = SelectField(u'标准', choices=zip(list(zip(*(db.session.query(StandardAndSpe, StandardAndSpe.name).all()))[1]), list(zip(*(db.session.query(StandardAndSpe, StandardAndSpe.name).all()))[1])))

	# tool = SelectMultipleField(u'工具', choices=zip(list(zip(*(db.session.query(Tool, Tool.name).all()))[1]), list(zip(*(db.session.query(Tool, Tool.name).all()))[1])), option_widget= widgets.CheckboxInput)

	# organization = SelectMultipleField(u'组织或学校', choices=zip(list(zip(*(db.session.query(Organization, Organization.name).all()))[1]), list(zip(*(db.session.query(Organization, Organization.name).all()))[1])))
	# knowledge = SelectMultipleField(u'知识点', choices=zip(list(zip(*(db.session.query(KnowledgeElement, KnowledgeElement.name).all()))[1]), list(zip(*(db.session.query(KnowledgeElement, KnowledgeElement.name).all()))[1])))

	submit = SubmitField(u'提交')

class submitForm(Form):
	submit = SubmitField(u'提交')
