from flask import Flask,redirect,render_template,flash,request
from flask_sqlalchemy import SQLAlchemy
from flask.globals import request, session
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,logout_user,login_user,login_manager,LoginManager,current_user
from flask.helpers import url_for
 

import json

#mydb connection
local_server=True
app=Flask(__name__)
app.secret_key="sudhan"

#this is user hashcode
login_manager=LoginManager(app)
login_manager.login_view='login'

#app.config['SQLALCHEMY_DATABASE_URI']='mysql://username:password@localhost/databasename'
app.config['SQLALCHEMY_DATABASE_URI']='mysql://root:@localhost/covid'
db=SQLAlchemy(app)

with open('backend/config.json','r') as c:
    params=json.load(c)["params"]


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    srfid=db.Column(db.String(20),unique=True)
    email=db.Column(db.String(50))
    dob=db.Column(db.String(1000))

class Hospitaluser(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20))
    email=db.Column(db.String(50))
    password=db.Column(db.String(1000))

class Hospitaldata(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    hcode=db.Column(db.String(20),unique=True)
    hname=db.Column(db.String(100))
    normalbed=db.Column(db.Integer)
    hicubed=db.Column(db.Integer)
    icubed=db.Column(db.Integer)
    vbed=db.Column(db.Integer)


@app.route("/")
def home():
    return render_template("index.html")



@app.route('/signup',methods=['POST','GET'])
def signup():
    if request.method=="POST":
        srfid=request.form.get('srf')
        email=request.form.get('email')
        dob=request.form.get('dob')
        #print(srfid,email,dob)
        encpassword=generate_password_hash(dob)
        user=User.query.filter_by(srfid=srfid).first()
        emailuser=User.query.filter_by(email=email).first()
        if user or emailuser:
            flash("Email or srfid is already taken","warning")
            return render_template("usersignup.html")

        new_user=db.engine.execute(f"INSERT INTO `user` (`srfid`,`email`,`dob`) VALUES ('{srfid}','{email}','{encpassword}')")
        
        flash("SignUP Success Kindly Login","success")
        return render_template("userlogin.html")
   
    return render_template("/usersignup.html")

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method=="POST":
        srfid=request.form.get('srf')
        dob=request.form.get('dob')
        user=User.query.filter_by(srfid=srfid).first()

        if user and check_password_hash(user.dob,dob):
            login_user(user)
            flash("login Success","info")
            return render_template("index.html")
           
        else:
            flash("Invalid Credentials","danger")
            return render_template("userlogin.html")
    
    return render_template("/userlogin.html")

@app.route('/hospitallogin',methods=['POST','GET'])
def hospitallogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Hospitaluser.query.filter_by(email=email).first()
        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","info")
            return render_template("index.html")
        else:
            flash("Invalid Credentials","danger")
            return render_template("hospitallogin.html")


    return render_template("hospitallogin.html")

@app.route('/admin',methods=['POST','GET'])
def admin():
    if request.method=="POST":
        username=request.form.get('username')
        password=request.form.get('password')
        print(username,password)
        if(username==params['user'] and password==params['password']):
            session['user']=username
            flash("login success","info")
            return render_template("addHosUser.html")
        else:
            flash("Invalid Credentials","danger")

    return render_template("admin.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))


@app.route('/addHospitalUser',methods=['POST','GET'])
def hospitalUser():
   
    if('user' in session and session['user']==params['user']):
      
        if request.method=="POST":
            hcode=request.form.get('hcode')
            email=request.form.get('email')
            password=request.form.get('password')        
            encpassword=generate_password_hash(password)  
            hcode=hcode.upper()
            emailUser=Hospitaluser.query.filter_by(email=email).first()
            if  emailUser:
                flash("Email or srif is already taken","warning")
         
            new_user=db.engine.execute(f"INSERT INTO `hospitaluser` (`hcode`,`email`,`password`) VALUES ('{hcode}','{email}','{encpassword}') ")
            flash("Data Inserted","warning")
            
        return render_template("addHosUser.html")
    else:
        flash("Login and try Again","warning")
        return redirect('/admin')
    







#testing wheather db is connected or not
@app.route("/test")
def test():
    try:
        a= Test.query.all()
        print(a)
        return f'My Database is connected'
    except Exception as e:
        print(e)
        return 'My DATABASE is NOT Connected{e}'


@app.route("/logoutadmin")
def logoutadmin():
    session.pop('user')
    flash("You are logout admin", "primary")

    return redirect('/admin')   

@app.route("/addhospitalinfo",methods=['POST','GET'])
def addhospitalinfo():  

    if request.method=="POST":
        hcode=request.form.get('hcode')
        hname=request.form.get('hname')
        nbed=request.form.get('normalbed')
        hbed=request.form.get('hicubeds')
        ibed=request.form.get('icubeds')
        vbed=request.form.get('ventbeds')
        hcode=hcode.upper()
        huser=Hospitaluser.query.filter_by(hcode=hcode).first()
        hduser=Hospitaldata.query.filter_by(hcode=hcode).first()
        if hduser:
            flash("Data is already Present you can update it..","primary")
            return render_template("hospitaldata.html")
        if huser:            
            db.engine.execute(f"INSERT INTO `hospitaldata` (`hcode`,`hname`,`normalbed`,`hicubed`,`icubed`,`vbed`) VALUES ('{hcode}','{hname}','{nbed}','{hbed}','{ibed}','{vbed}')")
            flash("Data Is Added","primary")
        else:
            flash("Hospital Code not Exist","warning")
    return render_template("hospitaldata.html")  


app.run(debug=True)

