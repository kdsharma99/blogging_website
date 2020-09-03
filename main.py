from flask import Flask,render_template,session,redirect,flash
from flask_sqlalchemy import SQLAlchemy
from flask import request
from flask_mail import Mail
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename
import math
with open("config.json",'r') as c:
    params=json.load(c)["params"]
local_server=True    
app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config.update(
    MAIL_SERVER="smtp.gmail.com",
    MAIL_PORT="465",
    MAIL_USE_SSL=True,
    MAIL_USERNAME="infinitedimension7@gmail.com",
    MAIL_PASSWORD="premlata3"
)
mail=Mail(app)
if params["local_server"]==True:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["loacal_uri"]
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params["prod_uri"]
db = SQLAlchemy(app)
class messages(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), unique=False, nullable=False)
    email = db.Column(db.String(50), unique=False, nullable=False)
    phone = db.Column(db.String(12),  nullable=False)
    date = db.Column(db.String(12), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
class posts(db.Model):
    Sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), unique=False, nullable=False)
    slug = db.Column(db.String(50), unique=False, nullable=False)
    content = db.Column(db.String(500),  nullable=False)
    pickup = db.Column(db.String(50), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    date = db.Column(db.String(12), nullable=False)
    category = db.Column(db.String(12), nullable=False)
    img_file = db.Column(db.String(50), nullable=False)
@app.route('/')
def home():
    postss=posts.query.filter_by().all()
    last=math.ceil(len(postss)/int(params["No_of_posts"]))
    page=request.args.get('page')
    if not str(page).isnumeric():
        page=1
    page=int(page)
    postss=postss[(page-1)*int(params["No_of_posts"]):(page-1)*int(params["No_of_posts"])+int(params["No_of_posts"])]
    if page==1:
        prev="#"
        nxt="/?page="+str(page+1)
    elif page==last:
        prev="/?page="+str(page-1)
        nxt="#"
    else:
        prev="/?page="+str(page-1)
        nxt="/?page="+str(page+1)
    return render_template("index.html",params=params,postss=postss,prev=prev,nxt=nxt)
@app.route('/about')
def about():
    return render_template("about.html",params=params)
@app.route('/contact', methods = ['GET','POST'])
def contact():
    if request.method=='POST':
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        entry=messages(Name=name,email=email,phone=phone,date=datetime.now(),msg=message)
        db.session.add(entry)
        db.session.commit()
        mail.send_message(name + " want to gave you message from blog",sender=email,recipients=[params["admin"]],body=message+"\n"+phone+"\n"+email)
        flash("Your message sent. We will contact you soon","success")
    return render_template("contact.html",params=params)
@app.route('/post/<string:post_slug>',methods=['GET'])
def post_route(post_slug):
    post=posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html",params=params,post=post)
@app.route('/dashboard-login',methods=['GET','POST'])
def dashboard_login():
    if 'user' in session and session['user']==params['admin_login']:
        post=posts.query.filter_by().all()
        return render_template("dashboard.html",params=params,post=post)
    if request.method=='POST':
        username=request.form.get('uname')
        password=request.form.get('pswd')
        if username==params['admin_login'] and password==params['admin_pswd']:
            session['user']=username
            post=posts.query.all()
            return render_template("dashboard.html",params=params,post=post)
        else:
            return render_template("dashboard-login.html",params=params)
    else:
        return render_template("dashboard-login.html",params=params)
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'user' in session and session['user']==params['admin_login']:
        post=posts.query.filter_by().all()
        return render_template("dashboard.html",params=params,post=post)
@app.route('/add',methods=['GET','POST'])
def add():
    if 'user' in session and session['user']==params['admin_login']:
        if request.method=='POST':
            ttl1=request.form.get('tittle')
            ttl2=request.form.get('slug')
            ttl3=request.form.get('author')
            ttl4=request.form.get('category')
            ttl5=request.form.get('content')
            ttl6=request.form.get('pickup')
            ttl7=request.form.get('imgfile')
            post=posts(title=ttl1,slug=ttl2,content=ttl5,pickup=ttl6,author=ttl3,date=datetime.now(),category=ttl4,img_file=ttl7)
            db.session.add(post)
            db.session.commit()
            flash("Added","success")
            return redirect('/add')
        return render_template("add.html",params=params) 
@app.route('/edit/<string:sno>',methods=['GET','POST'])
def edit(sno):
    if 'user' in session and session['user']==params['admin_login']:
        postss=posts.query.filter_by(Sno=sno).first()
        if request.method=='POST':
            postss.title=request.form.get('tittle')
            postss.slug=request.form.get('slug')
            postss.author=request.form.get('author')
            postss.category=request.form.get('category')
            postss.content=request.form.get('content')
            postss.pickup=request.form.get('pickup')
            postss.img_file=request.form.get('imgfile')
            db.session.commit()
            flash("Edited","success")
            return redirect('/edit/'+sno)
            return render_template("edit.html",params=params,postss=postss) 
        return render_template("edit.html",params=params,postss=postss)
@app.route('/uploader',methods=['GET','POST'])
def upload():
    if 'user' in session and session['user']==params['admin_login']:
        post=posts.query.filter_by().all()
        if request.method=='POST':
            f=request.files['file']
            f.save(os.path.join(params['upload_location'],secure_filename(f.filename)))
            flash("Uploaded","success")
        return render_template("dashboard.html",params=params,post=post)
@app.route('/logout')
def logout():
    session.pop('user')
    flash("Logged Out","success")
    return redirect('/dashboard-login')
@app.route('/delete/<string:sno>',methods=['GET','POST'])
def delete(sno):
    if 'user' in session and session['user']==params['admin_login']:
        post=posts.query.filter_by(Sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        flash("Deleted","success")
    return redirect('/dashboard-login')
app.run(debug=True)
