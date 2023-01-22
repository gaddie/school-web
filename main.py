from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from wtforms import StringField, SubmitField, PasswordField, IntegerField
from wtforms.validators import DataRequired, URL
import email
from werkzeug.security import generate_password_hash, check_password_hash
from distutils.log import error
from email_validator import validate_email, EmailNotValidError
from flask_bootstrap import Bootstrap
import re
import ssl
import random
from email.message import EmailMessage
import smtplib
from sqlalchemy.orm import sessionmaker
from flask_migrate import Migrate
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from wtforms import Form, SelectField




app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)


# create a session
session = db.session

migrate = Migrate(app, db)



login_manager = LoginManager()
login_manager.init_app(app)

Base = declarative_base()

@login_manager.user_loader
def load_user(user):
    return Students.query.get(int(user))


# ---------- DATABASE TABLES ------------
# ************ admins DB ****************

# class Admins(UserMixin, db.Model):
#     __tablename__ = 'admins'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     f_name = db.Column(db.String(1000))
#     l_name = db.Column(db.String(1000))
#     phone = db.Column(db.Integer, unique=True)
#     occupation = db.Column(db.String(100))


# with app.app_context(): 
#     db.create_all()   


# ************ lectures db **************
# class Lecturers(UserMixin, db.Model):
#     __tablename__ = 'lecturers'
#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(100), unique=True)
#     password = db.Column(db.String(100))
#     f_name = db.Column(db.String(1000))
#     l_name = db.Column(db.String(1000))
#     phone = db.Column(db.Integer, unique=True)

# with app.app_context(): 
#     db.create_all()   


# *************** departments ****************
# class Lecturers(UserMixin, db.Model):
#     __tablename__ = 'lecturers'
#     id = db.Column(db.Integer, primary_key=True)
#     department = db.Column(db.String(100), unique=True)
  

# with app.app_context(): 
#     db.create_all()   


# *************** grades ****************
# class Grade(UserMixin, db.Model):
#     __tablename__ = 'grades'
#     id = db.Column(db.Integer, primary_key=True)


# with app.app_context(): 
#     db.create_all()   


# ************ notice board *************
# class Anouncement(UserMixin, db.Model):
#     __tablename__ = 'anouncement'
#     id = db.Column(db.Integer, primary_key=True)
#     date = db.Column(db.String(100))
#     event = db.Column(db.String(1000))

# with app.app_context(): 
#     db.create_all()   


# ************* students DB **************
class Students(UserMixin, db.Model):
    __tablename__ = "students"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    f_name = db.Column(db.String(1000))
    l_name = db.Column(db.String(1000))
    phone = db.Column(db.Integer, unique=True)
    reg_no = db.Column(db.String(50), unique=True)

    fees = db.relationship("Fees", back_populates="student")

with app.app_context(): 
    db.create_all()


class Fees(UserMixin, db.Model):
    __tablename__ = 'fee'
    id = db.Column(db.Integer, primary_key=True)
    fee_balance = db.Column(db.Integer)

    student_id = db.Column(db.Integer, db.ForeignKey('students.id'))
    student = relationship("Students", back_populates="fees")

with app.app_context(): 
    db.create_all()



# ------------- FORMS ----------------

# *********** students registration form ***********
class RegisterForm(FlaskForm):
    f_name = StringField("First name", validators=[DataRequired()])
    l_name = StringField("Last name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), email.utils.parseaddr])
    reg_no = StringField("Reg_no", validators=[DataRequired()])
    phone = IntegerField("Phone", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Register")


# students login form
class StudentsLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), email.utils.parseaddr])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log in") 


# students verification code form
class StudentsResetForm(FlaskForm):
    code = IntegerField("Enter the verification code", validators=[DataRequired()])
    submit = SubmitField("Verify") 


# enter email form if the user is not loggen in 
class EmailForm(FlaskForm):
    email = StringField("Please enter the email", validators=[DataRequired(), email.utils.parseaddr])
    submit = SubmitField("Send code") 


# students reset password form
class PasswordResetForm(FlaskForm):
    new_password = PasswordField("Enter your new password", validators=[DataRequired()])
    submit = SubmitField("Cornfirm") 


# VALIDARION OF EMAIL
def check(email):
    try:
      # validate and get info
        v = validate_email(email)
        # replace with normalized form
        email = v["email"] 
        return True
    except EmailNotValidError as e:
        # email is not valid, exception message is human-readable
        flash('The email is invalid. An email must contain atleast one @ sign')
        return redirect(url_for("register", error=error))

 
for i in range(0, 4):
    random_number = random.randint(1234,9876)

validation_code = random_number


class MyForm(Form):
    choices = [('option1', 'Male'), ('option2', 'Option 2'), ('option3', 'Option 3')]
    select = SelectField('Select an option:', choices=choices)


def send_email_config(student_email):
        email_sender = "dailydeals9396@gmail.com"
        email_receiver = student_email
        email_password = "byxbqcsrmwkulknk"

        subject = "PASSWORD RESET"
        body = f"VERIFICATION CODE {validation_code}"

        em = EmailMessage()
        em["Subject"] = subject
        em["From"] = email_sender
        em["To"] = email_receiver
        em.set_content(body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(email_sender, email_password)
            server.sendmail(email_sender, email_receiver, em.as_string())
        
        


# ************password reset route ************
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    student_email = current_user.email
    password_form = PasswordResetForm()

    if request.method == 'POST':
        new_password = password_form.new_password.data

         # VALIDATION OF PASSWORD
        if len(new_password) < 8:
            flash("Your password must be atleast 8 characters.")
            return redirect(url_for("reset_password", error=error))
        elif re.search('[0-9]',new_password) is None:
            flash("Your password must have at least 1 number")
            return redirect(url_for("reset_password", error=error))
        elif re.search('[A-Z]',new_password) is None:
            flash("Your password must have at least 1 uppercase letter.")
            return redirect(url_for("reset_password", error=error))
        else:
            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
            student = Students.query.filter_by(email=student_email).first()
            student.password = hashed_password
            db.session.commit()
        return redirect(url_for("home"))
        
    return render_template("password_reset.html", student_email=student_email, form=password_form)


# ********** SENDING EMAIL FOR VALIDATION **********
@app.route('/send_email', methods=["GET", "POST"])
def send_email(): 
    password_form = PasswordResetForm()
    
    if not current_user.is_authenticated:
        form = EmailForm()

        # if request.method == 'POST':
        #     email = form.email.data
            
            

        #     student_email = session.query(Students).filter(Students.email == email).first().email


        #     if student_email:
        #         send_email_config(email)

        #         student_form = StudentsResetForm()
        #         return render_template("reset.html", student_email=student_email, form=student_form)
        #     else:
        #         flash("The email is not registered, please enter a registered email")
        #         return redirect(url_for("send_email"))

        # return render_template("send_email.html", form=form)


        if request.method == 'POST':
            email = form.email.data
        

            # check(email)
            # student_email = Students.query.filter_by(email=email).first().email
            student_email = session.query(Students).filter(Students.email == email).first()

            if student_email:
                send_email_config(email)

                student_form = StudentsResetForm()
                return render_template("reset.html", student_email=student_email, form=student_form)


            if request.method == 'POST':
                student_form = StudentsResetForm()
                user_code = student_form.code.data

                if request.method == 'POST':
                    new_password = password_form.new_password.data
                    # return render_template("password_reset.html", student_email=student_email, form=password_form)
                    if user_code == validation_code:
                        password_form = PasswordResetForm()
                        # VALIDATION OF PASSWORD
                        if len(new_password) < 8:
                            flash("Your password must be atleast 8 characters.")
                            return redirect(url_for("reset_password", error=error))
                        elif re.search('[0-9]',new_password) is None:
                            flash("Your password must have at least 1 number")
                            return redirect(url_for("reset_password", error=error))
                        elif re.search('[A-Z]',new_password) is None:
                            flash("Your password must have at least 1 uppercase letter.")
                            return redirect(url_for("reset_password", error=error))
                        else:
                            hashed_password = generate_password_hash(new_password, method='pbkdf2:sha256', salt_length=8)
                            student = Students.query.filter_by(email=student_email).first()
                            student.password = hashed_password
                            db.session.commit()
                            return redirect(url_for("home"))

                else:
                    flash("The code is incorrect, please enter the correct code")

                if request.method == 'POST':
                    new_password = password_form.new_password.data
                    return render_template("password_reset.html", student_email=student_email, form=password_form)


              


               

            else:
                flash("The email is not registered, please enter a registered email")
                return redirect(url_for("send_email"))
        return render_template("send_email.html", form=form)
        
    else:
        student_email = current_user.email
        send_email_config(student_email)
    
        return redirect(url_for("verify_code"))


# ************* home route **************
@app.route('/')
def home():
    form = MyForm()
    return render_template("index.html", form=form)


# ********** reseting password route ***********
@app.route('/verify_code', methods=['POST', 'GET'])
def verify_code():
    student_email = current_user.email
    form = StudentsResetForm()

    if request.method == 'POST':
        user_code = form.code.data

        if user_code == validation_code:
            return redirect(url_for("reset_password"))

        else:
            flash("The code is incorrect, please enter the correct code")

    return render_template("reset.html", student_email=student_email, form=form)


# ************ students login route ************
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = StudentsLoginForm()
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        student = Students.query.filter_by(email=email).first()
        if student:
            if check_password_hash(student.password, password):
                login_user(student)
                return redirect(url_for("students_page", name=student.f_name))
            else:
                flash("Please check your password")
                return redirect(url_for("login", error=error))
        else:
            flash("Please check your email!")
            return redirect(url_for("login", error=error))

    return render_template("login.html", form=form)


# ************* register route ****************
@app.route('/register', methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if request.method == "POST":

        # check if email already exists in db
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        

        check(email)

        # VALIDATION OF PASSWORD
        if len(password) < 8:
            flash("Your password must be atleast 8 characters.")
            return redirect(url_for("register", error=error))
        elif re.search('[0-9]',password) is None:
            flash("Your password must have at least 1 number")
            return redirect(url_for("register", error=error))
        elif re.search('[A-Z]',password) is None:
            flash("Your password must have at least 1 uppercase letter.")
            return redirect(url_for("register", error=error))

        if len(phone) != 10:
            flash('The phone number length should be 10')

        elif Students.query.filter_by(email=email).first():
            flash("Email already exists!")
            return redirect(url_for("register", error=error))
        elif Students.query.filter_by(phone=phone).first():
            flash("Phone number already exists!")
            return redirect(url_for("register", error=error))
        
        else:
            # hashing a password
            hash_and_salted_password = generate_password_hash(
                request.form.get('password'),
                method='pbkdf2:sha256',
                salt_length=8
            )

            new_user = Students(
                email=request.form.get('email'),
                f_name=request.form.get('f_name'),
                l_name=request.form.get('l_name'),
                password=hash_and_salted_password,
                phone=request.form.get('phone'),
                reg_no=request.form.get('reg_no')
            )

            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)

            return redirect(url_for("home"))

    return render_template("register.html", form=form)



# ********** logout route ***********
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route('/students_page')
def students_page():
    # fee_balance = Fees.query.all()
    return render_template('students_menu.html', current_user=current_user)


@app.route('/admin')
def admin():
    return render_template('admin.html')


if __name__ == "__main__":
    app.run(debug=True, port=8000)


# change the password route for when the user is not logged in

