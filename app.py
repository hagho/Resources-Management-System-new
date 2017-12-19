# coding: UTF-8
from flask import Flask, render_template, g, session, flash, redirect, url_for, abort, request, send_from_directory
from flask.ext.bootstrap import Bootstrap
from flask.ext.login import LoginManager
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import *
from Model import Post, db, PostComment
from Model import User, StandardAndSpe, Tool, Organization,KnowledgeElement,KELinker,Course
from Model import LResource,Res_Std, Res_Tool,Res_Org,Res_KE 
from werkzeug import secure_filename
import os
import sys
from functools import wraps
import time
import datetime
import ast
from sqlalchemy import or_, func

reload(sys) 
sys.setdefaultencoding('utf-8')
basedir = os.getcwd()
#init
app = Flask(__name__)
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soaDB.db'
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SECRET_KEY'] = '1122334556'

db.app = app
db.init_app(app)
bootstrap = Bootstrap(app)
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'signin'
typeMap = [u'无', u'教学计划', u'教学大纲', u'教学方案', u'教材', u'课件', u'案例描述', u'案例参考答案', u'试验题目', u'实验指导', u'实验报告', u'试卷', u'试卷答案', u'练习']
formatMap = [u'无', u'文档', u'视频', u'音频']
#permission control
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_anonymous():
            abort(403)
        if not current_user.getRole == ROLE_AD:
            abort(403)
        return f(*args, **kwargs)
    return decorated

def moderator_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_user.is_anonymous():
            abort(403)

        if current_user.getRole() == 0 :
            abort(403)

        return f(*args, **kwargs)
    return decorated




#views
@app.before_request
def before_request():
   g.user = current_user


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    name = session.get('name')
    user = g.user
    latest = db.session.query(LResource).order_by(LResource.id.desc()).limit(5)
    posts = db.session.query(Post).order_by(Post.id.desc()).limit(10)
    uploader = []
    for entry in latest:
        print entry.id
        uploader.append(User.query.filter_by(id = entry.id).first())
        print uploader[0]

    if g.user is not None:
        return render_template('index.html', user = user, name = name, latest = latest, uploader=uploader, posts = posts)
    return render_template('index.html', user = user, name = None, latest = latest,uploader = uploader, posts=posts)



@app.route('/signin',methods=['GET', 'POST'])
def signin():
    name = None
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = SigninForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        if user is not None:
            if user.password == form.password.data:
                flash(u'用户'+form.username.data +'成功登陆!', 'success')
                session['name'] = form.username.data
                login_user(user)
                latest = db.session.query(LResource).order_by(LResource.id.desc()).limit(5)
                posts = db.session.query(Post).order_by(Post.id.desc()).limit(10)
                uploader = []
                for entry in latest:
                    print entry.id
                    uploader.append(User.query.filter_by(id = entry.id).first().username)
                return render_template('index.html', name = session.get('name'), user = user,latest = latest, uploader=uploader, posts=posts)
        else:
            flash(u'Fail to log in', 'error')
            return render_template('signin.html', form=form, name = name)
    return render_template('signin.html', form=form, name = name)

@app.route('/signup',methods=['GET', 'POST'])
def signup():
    name = session.get('name')
    form = UserForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username = form.username.data).first()
        email = User.query.filter_by(email = form.email.data).first()
        if user is None and email is None:
            user = User(username = form.username.data, email = form.email.data, password = form.password.data)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
            session['name'] = form.username.data
            flash(u'Successully Sign up!', 'success')
            login_user(user)
            posts = db.session.query(Post).order_by(Post.id.desc()).limit(10)
            latest = db.session.query(LResource).order_by(LResource.id.desc()).limit(5)
            uploader = []
            for entry in latest:
                print entry.id
                uploader.append(User.query.filter_by(id = entry.id).first().username)
            return render_template('index.html', name = session.get('name'), user = user,latest = latest, uploader=uploader, posts=posts)
        else:
            if user is not None:
                flash(u'用户名已存在', 'error')
            if email is not None:
                flash(u'邮箱已存在','error')
            return render_template('signup.html', form = form, user = g.user, name = session.get('name'))
        session['name'] = form.username.data
        form.username.data = ''
        return redirect(url_for('index'))
        # return render_template('index.html', name = session.get('name'), user = user,latest = latest, uploader=uploader, posts=posts)
    return render_template('signup.html', form=form, name = name)

@app.route('/upload', methods = ['GET', 'POST'])
#@moderator_required
def upload(): 
    form = UploadForm()
    uploader_id = current_user.get_id()
    stds = list(zip(*(db.session.query(StandardAndSpe, StandardAndSpe.name).all()))[1])
    tools = list(zip(*(db.session.query(Tool, Tool.name).all()))[1])
    orgs = list(zip(*(db.session.query(Organization, Organization.name).all()))[1])
    knows = list(zip(*(db.session.query(KnowledgeElement, KnowledgeElement.name).all()))[1])
    if form.validate_on_submit():
        stdList = request.form.getlist('std')
        orgList = request.form.getlist('org')
        toolList = request.form.getlist('tool')
        keList = request.form.getlist('know')

        newstdList = request.form.getlist('newstd')
        neworgList = request.form.getlist('neworg')
        newtoolList = request.form.getlist('newtool')
        newkeList = request.form.getlist('newknow')

        newstddescList = request.form.getlist('newstddesc')
        neworgdescList = request.form.getlist('neworgdesc')
        newtooldescList = request.form.getlist('newtooldesc')
        newkedescList = request.form.getlist('newknowdesc')

        flag = 0
        if (stdList == [] and newstdList == []):
            flag = 1
            flash(u'未填写标准或自定义标准！', 'error')

        if (orgList == [] and neworgList == []):
            flag = 1
            flash(u'未填写组织、学校或自定义组织、学校！', 'error')

        if (toolList == [] and newtoolList == []):
            flag = 1
            flash(u'未填写工具或自定义工具！', 'error')

        if (keList == [] and newkeList == []):
            flag = 1
            flash(u'未填写知识点或自定义知识点！', 'error')
        
        if flag == 1: 
            render_template('upload.html', form = form, name = session['name'], knows = knows, stds = stds, tools = tools, orgs = orgs)
        else:
            std_id = []
            org_id = []
            tool_id = []
            ke_id = []
            for i in range(len(neworgList)):
                resorg = Organization(neworgList[i], neworgdescList[i])
                db.session.add(resorg)
                db.session.commit()
                org_id.append(Organization.query.filter_by(name = neworgList[0]).first().id)
            for i in range(len(newtoolList)):
                restool = Tool(newtoolList[i], newtooldescList[i])
                db.session.add(restool)
                db.session.commit()
                tool_id.append(Tool.query.filter_by(name = newtoolList[0]).first().id)
            for i in range(len(newstdList)):
                resstd = StandardAndSpe(newstdList[i], newstddescList[i])
                db.session.add(resstd)
                db.session.commit()
                std_id.append(StandardAndSpe.query.filter_by(name = newstdList[0]).first().id)

            for x in stdList:
                std_id.append(StandardAndSpe.query.filter_by(name = x).first().id)
            for x in orgList:
                org_id.append(Organization.query.filter_by(name = x).first().id)
            for x in toolList:
                tool_id.append(Tool.query.filter_by(name = x).first().id)
            for x in keList:
                ke_id.append(KnowledgeElement.query.filter_by(name = x).first().id)

            attach = []
            attach.append(ke_id)
            newkeList = zip(newkeList, newkedescList)
            attach.append(newkeList)
            course_id = Course.query.filter_by(name = form.course.data).first().id
            types = form.types.data
            format = form.format.data
            filename = secure_filename(form.file.data.filename)
            t = time.time()
            form.file.data.save('uploads/' + str(format) + '/' + str(types) + '/' + str(t) + filename)
            address = 'uploads/' + str(format) + '/' + str(types) + '/' + str(t) + filename

            resource = LResource(name = form.name.data, types = int(types), format = int(format), course_id = int(course_id), url = form.url.data, author = form.author.data, uploader_id = int(uploader_id), desc = form.desc.data, addr = address, updatetime = datetime.datetime.now())
            db.session.add(resource)
            db.session.commit()
            res_id = LResource.query.filter_by(name = form.name.data).first().id
            attach.append(res_id)
            for x in std_id:
                standard = Res_Std(res_id, x)
                db.session.add(standard)
            db.session.commit()

            for x in org_id:
                organization = Res_Org(res_id, x)
                db.session.add(organization)
            db.session.commit()

            for x in tool_id:
                tool = Res_Tool(res_id, x)
                db.session.add(tool)
            db.session.commit()

            return redirect(url_for('attachment', attach = attach))
    
    return render_template('upload.html', form = form, name = session['name'], knows = knows, stds = stds, tools = tools, orgs = orgs)


@app.route('/upload/<attach>', methods = ['GET', 'POST'])
#@moderator_required
def attachment(attach):
    form = submitForm()
    attach = ast.literal_eval(attach)
    res_id = attach[2]
    know = attach[0]
    keName = []
    for k in know:
        keName.append(KnowledgeElement.query.filter_by(id = int(k)).first().name)
 
    newke = attach[1]
    uploader_id = current_user.get_id()

    if form.validate_on_submit():
        degreeList = request.form.getlist('degree')
        descList = request.form.getlist('desc')
        newdegreeList = request.form.getlist('newdegree')
        newdescList = request.form.getlist('newdesc')
        if len(degreeList) != len(keName) or len(descList) != len(keName) != len(newdescList) != len(newke) or len(newdegreeList) != len(newke):
            flash(u'有项目未填写or多选了！', 'error')
            return render_template('attachment.html', form = form, keName = keName, newke = newke, name = session['name'])
        else:
            new_keid = []
            for x in newke:
                ke = KnowledgeElement(x[0], 0, 0, x[1])
                db.session.add(ke)
                db.session.commit()
                new_keid.append(KnowledgeElement.query.filter_by(name = x[0]).first().id)

            for i in range(len(know)):
                reske = Res_KE(int(res_id), int(know[i]), int(degreeList[i]), descList[i])
                db.session.add(reske)
            db.session.commit()

            for i in range(len(new_keid)):
                reske = Res_KE(int(res_id), int(new_keid[i]), int(newdegreeList[i]), newdescList[i])
                db.session.add(reske)
            db.session.commit()
            flash(u'Successfully Create Resource!', 'success')
            return redirect(url_for('upload'))
    
    return render_template('attachment.html', form = form, keName = keName, newke = newke, name = session['name'])

@app.route('/resource', methods = ['GET', 'POST'])
def search():
    form = SearchForm()
    # if form.validate_on_submit():
    # #     print form.title.data
    #     return redirect(url_for('search_results', query = form.title.data))
    standardList = list(zip(*(db.session.query(StandardAndSpe, StandardAndSpe.name).all()))[1])
    typesList = [('1', u'教学计划'), ('2',u'教学大纲'), ('3',u'教学方案'), ('4',u'教材'), ('5', u'课件'), ('6', u'案例描述'), ('7', u'案例参考答案'), ('8', u'试验题目'), ('9', u'实验指导'), ('10', u'实验报告'), ('11', u'试卷'), ('12', u'试卷答案'), ('13', u'练习')]
    formatList = [('1', u'文档'), ('2',u'视频'), ('3',u'音频')]
    courseList = list(zip(*(db.session.query(Course, Course.name).all()))[1])
    toolList = list(zip(*(db.session.query(Tool, Tool.name).all()))[1])
    types_format = {'资源类别':typesList, '资源格式':formatList, '课程名称':courseList, '标准名称':standardList, '工具名称':toolList}
    if request.method == "POST":
        if request.form['search_title'] == '':
            flash(u'请输入标题！','error')
        else:
            search_filter = {}
            search_filter.setdefault('types', [1,2,3,4])
            search_filter.setdefault('format',[1,2,3])
            for key in types_format.keys():
                if request.form.getlist(key):
                    if key == '资源类别':
                        newKey = 'types'
                    if key == '资源格式':
                        newKey = 'format'
                    if key == '课程名称':
                        newKey = 'course_id' 
                    if key == '标准名称':
                        newKey = 'standard'
                    if key == '工具名称':
                        newKey = 'tool'
                    search_filter[newKey] = request.form.getlist(key)
            session['search_filter'] = search_filter
            return redirect(url_for('search_results', query = request.form['search_title'], search_filter=search_filter))
    return render_template('resource.html', form = form, name = session.get('name'), types_format=types_format)


@app.route('/search_results/<query>')
def search_results(query):
    search_filter = request.args['search_filter']
    search_filter = session['search_filter']
    # print "LOOK AT ME"
    # print search_filter
    results = LResource.query.filter(or_(LResource.name.like('%'+query+'%'), LResource.types in search_filter['types'], LResource.format in search_filter['format'])).group_by(LResource.name).all()
    # newResults = []
    # for result in results:
    #     for key in search_filter.keys():
    #         if key != 'tool' and key != 'standard':
    #             if eval(result).key in search_filter[key]:
    #                 newResults.append(result)
    results_name = []
    results_type = []
    results_format = []
    results_id = []
    for result in results:
        results_name.append(result.name)
        results_type.append(typeMap[int(result.types)])
        results_format.append(formatMap[int(result.format)])
        results_id.append(int(result.id))

    length = len(results_id)
    return render_template('search_results.html', query = query, length = length, results_id = results_id, results_name = results_name, results_type = results_type, results_format = results_format, name = session.get('name'))

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/manage_resources',methods = ['GET', 'POST'])
def manage_resources():
    user_id = current_user.get_id()
    resources = list(zip(*(db.session.query(LResource, LResource.id, LResource.name, LResource.types, LResource.format, LResource.uptime, LResource.updatetime).filter_by(uploader_id = user_id).all()))[1:])
    resources = zip(*resources)
    for i in range(len(resources)):
        resources[i] = list(resources[i])
        print type(resources[i][4])
        resources[i][4] = resources[i][4].strftime('%Y-%m-%d %H:%M')
        resources[i][5] = resources[i][5].strftime('%Y-%m-%d %H:%M')
        resources[i][2] = typeMap[int(resources[i][2])]
        resources[i][3] = formatMap[int(resources[i][3])]

    return render_template('manage_resources.html', resources = resources, name = session['name'])

@app.route('/delete_res',methods = ['GET', 'POST'])
def delete_res():
    res = LResource.query.filter_by(id = request.form['resource']).first()
    uploader = res.uploader_id
    if str(current_user.get_id()) == str(uploader):
        os.remove(os.path.join(basedir, res.addr))
        db.session.delete(res)
        db.session.commit()
        flash(u'Successfully delete Resource!', 'success')
    else:
        flash(u'Fail to delete Resource!', 'error')

    return redirect('manage_resources')

@app.route('/update_res',methods = ['GET', 'POST'])
def update_res():
    user_id = current_user.get_id()

    return redirect(url_for('update', res_id=request.form['resource']))



@app.route('/update/<res_id>',methods = ['GET', 'POST'])
def update(res_id):
    res = LResource.query.filter_by(id = res_id).first()

    return redirect('manage_resources')


@app.route('/download', methods=['GET', 'POST'])
def download():
    res = LResource.query.filter_by(id = request.form['res_id']).first()
    addr = res.addr
    addr = addr.split('/')
    return send_from_directory(directory=addr[0]+'/'+addr[1]+'/'+addr[2], filename=addr[3])


@app.route('/resource_details/<res_id>',methods = ['GET', 'POST'])
def resource_details(res_id):
    res_id = int(res_id)+1
    res = LResource.query.filter_by(id = res_id).first()
    name = res.name
    desc = res.desc
    author = res.author
    types = typeMap[int(res.types)]
    format = formatMap[int(res.format)]
    up_id = res.uploader_id
    uploader = User.query.filter_by(id = up_id).first().username
    course_id = res.course_id
    course = Course.query.filter_by(id = course_id).first().name
    url = res.url
    uptime = res.uptime
    updatetime = res.updatetime
    stds = []
    std = Res_Std.query.filter_by(res_id = res_id).group_by(Res_Std.std_id).all()
    for i in std:
        stds.append(i.name)

    tools = []
    tool = Res_Tool.query.filter_by(res_id = res_id).group_by(Res_Tool.tool_id).all()
    for i in tool:
        tool.append(i.name)

    orgs = []
    org = Res_Org.query.filter_by(res_id = res_id).group_by(Res_Org.org_id).all()
    for i in org:
        orgs.append(i.name)

    kes = []
    ke = Res_KE.query.filter_by(res_id = res_id).group_by(Res_KE.ke_id).all()
    for i in ke:
        kes.append(i.name)
    return render_template('resource_details.html', name = session['name'], res_id = res_id, res_name = name, res_desc = desc, types = types, format = format, author = author, uploader = uploader, course = course, url = url, uptime = uptime, updatetime = updatetime)


@app.route('/signUpUser', methods=['POST'])
def signUpUser():
    user =  request.form['username'];
    password = request.form['password'];
    return json.dumps({'status':'OK','user':user,'pass':password});

@app.route('/management',methods = ['GET', 'POST'])
def management():
    coursenum = db.session.query(Course.id).count()
    toolnum = db.session.query(Tool.id).count()
    stdnum = db.session.query(StandardAndSpe.id).count()
    kenum = db.session.query(KnowledgeElement.id).count()
    usernum = db.session.query(User.id).count()
    renum = db.session.query(LResource.id).count()
    return render_template('management.html', coursenum = coursenum, toolnum = toolnum, stdnum =stdnum, kenum = kenum, usernum = usernum, renum = renum, name = session.get('name'))

@app.route('/management/user',methods = ['GET', 'POST'])
def updateUser():
    users = User.query.all()
    uid = []
    uname = []
    ue = []
    ur = []
    for user in users:
        uid.append(user.id) 
        uname.append(user.username)
        ue.append(user.email)
        ur.append(user.role)
    length = len(users)
    return render_template('updateUser.html', length = length, uids = uid, users = uname, emails = ue, roles = ur, name = session.get('name'))

@app.route('/management/resource',methods = ['GET', 'POST'])
def updateResource():
    resources = LResource.query.all()
    rid = []
    name = []
    desc = []
    res_type = []
    res_format = []
    up_id = []
    up_time = []
    for resource in resources:
        rid.append(resource.id)
        name.append(resource.name)
        desc.append(resource.desc)
        print resource.id
        up_id.append(User.query.filter_by(id = resource.uploader_id).first().username)
        up_time.append(resource.uptime)
        res_type.append(typeMap[int(resource.types)])
        res_format.append(formatMap[int(resource.format)])
    length = len(resources)
    return render_template('viewResource.html', length = length, res_uploader = up_id, up_time = up_time, rids = rid, resources = name, res_desc = desc, res_type = res_type, res_format = res_format, name = session.get('name'))

@app.route('/management/course',methods = ['GET', 'POST'])
def updateCourse():
    courses = Course.query.all()
    cid = []
    name = []
    desc = []
    for course in courses:
        cid.append(course.id)
        name.append(course.name)
        desc.append(course.desc)
    length = len(courses)
    return render_template('updateCourse.html', length = length, cids = cid, courses = name, c_desc = desc, name = session.get('name'))


@app.route('/management/organization',methods = ['GET', 'POST'])
def updateOrg():
    orgs = Organization.query.all()
    oid = []
    name = []
    desc = []
    for org in orgs:
        oid.append(org.id)
        name.append(org.name)
        desc.append(org.desc)
    length = len(orgs)
    return render_template('updateOrg.html', length = length, oids = oid, org = name, o_desc = desc, name = session.get('name'))

@app.route('/management/tool',methods = ['GET', 'POST'])
def updateTool():
    tools = Tool.query.all()
    tid = []
    name = []
    desc = []
    for tool in tools:
        tid.append(tool.id)
        name.append(tool.name)
        desc.append(tool.desc)
    length = len(tools)
    return render_template('updateTool.html', length = length, tids = tid, tool = name, t_desc = desc, name = session.get('name'))

@app.route('/management/standard',methods = ['GET', 'POST'])
def updateStd():
    stds = StandardAndSpe.query.all()
    sid = []
    name = []
    desc = []
    for std in stds:
        sid.append(std.id)
        name.append(std.name)
        desc.append(std.desc)
    length = len(stds)
    return render_template('updateStd.html', length = length, sids = sid, std = name, s_desc = desc, name = session.get('name'))

@app.route('/management/knowledge',methods = ['GET', 'POST'])
def updateKnow():
    kes = KnowledgeElement.query.all()
    kid = []
    name = []
    desc = []
    for ke in kes:
        kid.append(ke.id)
        name.append(ke.name)
        desc.append(ke.desc)
    length = len(kes)
    return render_template('updateKnowledge.html', length = length, kids = kid, ke = name, k_desc = desc, name = session.get('name'))


@app.route('/deleteUser',methods = ['GET', 'POST'])
def deleteUser():
    user = User.query.filter_by(id = request.form['user']).first()
    if user != None:
        db.session.delete(user)
        db.session.commit()

    return redirect('management/user')

@app.route('/upUser',methods = ['GET', 'POST'])
def levelUpUser():
    user = User.query.filter_by(id = int(request.form['user'])).first()
    if user != None:
        if user.role < 2:
            user.role = user.role + 1
            db.session.commit()

    return redirect('management/user')

@app.route('/downUser',methods = ['GET', 'POST'])
def levelDownUser():
    user = User.query.filter_by(id = int(request.form['user'])).first()
    if user != None:
        if user.role > 0:
            user.role = user.role - 1
            db.session.commit()

    return redirect('management/user')

@app.route('/deleteCourse',methods = ['GET', 'POST'])
def deleteCourse():
    course = Course.query.filter_by(id = request.form['course']).first()
    if course != None:
        db.session.delete(course)
        db.session.commit()
    return redirect('management/course')


@app.route('/addCourse',methods = ['GET', 'POST'])
def addCourse():

    return redirect('management/course')

@app.route('/deleteStd',methods = ['GET', 'POST'])
def deleteStd():
    std = StandardAndSpe.query.filter_by(id = request.form['standard']).first()
    if std != None:
        db.session.delete(std)
        db.session.commit()

    return redirect('management/standard')


@app.route('/addStd',methods = ['GET', 'POST'])
def addStd():

    return redirect('management/standard')

@app.route('/deleteKnowledge',methods = ['GET', 'POST'])
def deleteKnowledge():
    ke = KnowledgeElement.query.filter_by(id = request.form['knowledge']).first()
    if ke != None:
        db.session.delete(ke)
        db.session.commit()

    return redirect('management/knowledge')


@app.route('/addKnowledge',methods = ['GET', 'POST'])
def addKnowledge():

    return redirect('management/knowledge')

@app.route('/deleteOrg',methods = ['GET', 'POST'])
def deleteOrg():
    org = Organization.query.filter_by(id = request.form['organization']).first()
    if org != None:
        db.session.delete(org)
        db.session.commit()

    return redirect('management/organization')


@app.route('/addOrg',methods = ['GET', 'POST'])
def addOrg():

    return redirect('management/organization')

@app.route('/deleteTool',methods = ['GET', 'POST'])
def deleteTool():
    tool = Tool.query.filter_by(id = request.form['tool']).first()
    if tool != None:
        db.session.delete(tool)
        db.session.commit()

    return redirect('management/tool')


@app.route('/addTool',methods = ['GET', 'POST'])
def addTool():

    return redirect('management/tool')


@app.route('/talk', methods=['GET', 'POST'])
def talk():
    if request.method == 'POST':
        if request.form['post_content'] != "":
            cont = request.form['post_content']
            locat = 0
            addTalk(cont, locat)
            return redirect(url_for('talk'))

    post = Post.query.all()
    post_id = []
    post_contents = []
    post_like = []
    comment_num = []
    # for x in post:
    #   post_id.append(str(x.id))
    #   post_contents.append(x.content)
    #   post_like.append(x.like_num)
    #   comment_num.append(len(PostComment.query.filter_by(post_id = int(x.id)).all()))
    for x in range(0,len(post))[::-1]:
        post_id.append(str(post[x].id))
        post_contents.append(post[x].content)
        post_like.append(post[x].like_num)
        comment_num.append(len(PostComment.query.filter_by(post_id = int(post[x].id)).all()))
    length = len(post)
    return render_template('about.html', post_id = post_id, comment_num = comment_num, post_like = post_like, post_contents = post_contents, length = length)


def addTalk(cont, locat):
    with app.app_context():
        newPost = Post(content=cont, location=locat)
        db.session.add(newPost)
        db.session.commit()


def addComment(comt, post_id):
    with app.app_context():
        newCom = PostComment(content=comt, post_id = post_id)
        db.session.add(newCom)
        db.session.commit()

@app.route('/comment/<post_id>', methods=['GET', 'POST'])
def comment(post_id):
    post = Post.query.filter_by(id = int(post_id)).first()

    if post != None:
        if request.method == 'POST':
            if request.form['comment_content'] != "":
                comt = request.form['comment_content']
                post_id = post.id
                addComment(comt, post_id)
                # addComment(comt,post_id)
                return redirect(url_for('comment', post_id = post_id))
        post = Post.query.filter_by(id = int(post_id)).first()
        post_content = post.content
        post_like = post.like_num
        post_time = post.create_time

        comments = PostComment.query.filter_by(post_id = int(post_id)).all()
        coms = []
        coms_time = []
        if comments != []:
            for x in comments:
                coms.append(x.content)
                coms_time.append(x.create_time)
        length = len(comments)
        post_id = str(post_id)
        return render_template('comment.html', length = length, comments = coms, comments_time = coms_time, post_content = post_content, post_time = post_time, post_like = post_like, post_id = post_id)
    return redirect(url_for('index'))

# define the methods for Like-adding requests '/addLike'
@app.route('/addLike', methods=['GET', 'POST'])
def addLike():
    if request.method == "POST":
        post_id = request.json['post_id']
        post = Post.query.filter_by(id = int(post_id)).first()
        post.like_num = post.like_num + 1
        db.session.commit()
        return jsonify(status="success")

# define the methods for Like-removing requests '/removeLike'
@app.route('/removeLike', methods=['GET', 'POST'])
def removeLike():
    if request.method == "POST":
        post_id = request.json['post_id']
        post = Post.query.filter_by(id = int(post_id)).first()
        post.like_num = post.like_num - 1
        db.session.commit()
        return jsonify(status="success")



if __name__ == '__main__':
    app.run(debug=True)
