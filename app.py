from flask.globals import request
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session
from project_orm import User,Patient
from flask import Flask,session,flash,redirect,render_template,url_for
from  utils import validate_email
from joblib import load
import pandas as pd

app=Flask(__name__)
app.secret_key="the basics of life with python"

def get_db():
    engine = create_engine('sqlite:///project_db.sqlite3')
    Session = scoped_session(sessionmaker(bind=engine))
    return Session()

@app.route('/',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        if email and validate_email(email):
            if password and len(password)>=5:
                try:
                    sess = get_db()
                    user = sess.query(User).filter_by(email=email,password=password).first()
                    if user:
                        session['isauth'] = True
                        session['email'] = user.email
                        session['id'] = user.id
                        session['name'] = user.name
                        del sess
                        flash('login successful','success')
                        return redirect('/home')
                    else:
                        flash('email or password is wrong','danger')
                except Exception as e:
                    flash(e,'danger')
            else:
                flash('password is wrong', 'danger')
        else:
            flash('email is wrong','danger')
    return render_template('index.html',title='login')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        cpassword = request.form.get('cpassword')
        if name and len(name) >= 3:
            if email and validate_email(email):
                if password and len(password)>=6:
                    if cpassword and cpassword == password:
                        try:
                            sess = get_db()
                            newuser = User(name=name,email=email,password=password)
                            sess.add(newuser)
                            sess.commit()
                            del sess
                            flash('registration successful','success')
                            return redirect('/')
                        except:
                            flash('email account already exists','danger')
                    else:
                        flash('confirm password does not match','danger')
                else:
                    flash('password must be of 6 or more characters','danger')
            else:
                flash('invalid email','danger')
        else:
            flash('invalid name, must be 3 or more characters','danger')
    return render_template('signup.html',title='register')

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    return render_template('forgot.html',title='forgot password')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if not session.get('isauth'):
        username = session.get('name')
        return redirect('/')
    if request.method == 'POST':
        name = request.form.get('name')
        age = request.form.get('age')
        sex = request.form.get('sex')
        steroid = request.form.get('steroid')
        antivirals = request.form.get('antivirals')
        fatigue = request.form.get('fatigue')
        malaise = request.form.get('malaise')
        anorexia = request.form.get('anorexia')
        liver_big = request.form.get('liver_big')
        liver_firm = request.form.get('liver_firm')
        spleen_palpable = request.form.get('spleen_palpable')
        spiders = request.form.get('spiders')
        ascites = request.form.get('ascites')
        varices = request.form.get('varices')
        bilirubin = request.form.get('Bilirubin')
        alk_phosphate = request.form.get('alk_phosphate')
        sgot = request.form.get('sgot')
        albumin = request.form.get('albumin')
        protime = request.form.get('protime')
        histology = request.form.get('histology')
        if name and len(name) >= 3:
            if int(age) <=100:
                try:
                    print('predicting')
                    sex_num = 1 if sex == 'Male' else 2
                    bilirubin = float(bilirubin)
                    alk_phosphate = float(alk_phosphate)
                    sgot = float(sgot)
                    albumin = float(albumin)
                    protime = float(protime)
                    histology = float(histology)
                    x = get_input(age=age,
                                sex=sex_num,
                                steriod=steroid,
                                antivirals=antivirals,
                                fatigue=fatigue, malaise=malaise,
                                anorexia=anorexia,
                                liver_big=liver_big,
                                liver_firm=liver_firm,
                                spleen_palpable=spleen_palpable,
                                spiders=spiders, 
                                ascites=ascites,
                                varices=varices,
                                bilirubin=bilirubin,
                                alk_phosphate=alk_phosphate, 
                                sgot=sgot,
                                albumin=albumin, 
                                protime=protime,
                                histology=histology
                                )
                    result = predict(x)
                    session['result'], is_hepatitis = result

                    db = get_db()
                    patient = Patient(name=name, age=age, steroid=bool(steroid),
                                      is_hepatitis=is_hepatitis,
                                    antivirals=bool(antivirals),
                                    fatigue=bool(fatigue), 
                                    malaise=bool(malaise),
                                    anorexia=bool(anorexia),
                                    is_liver_big=bool(liver_big),
                                    is_liver_firm=bool(liver_firm),
                                    spleen=bool(spleen_palpable),
                                    spiders=bool(spiders),
                                    iascites=bool(ascites),
                                    varices=bool(varices),
                                    bilirubin=bilirubin,
                                    alk_phosphate=alk_phosphate, sgot=sgot,
                                    albumin=albumin, protime=protime,
                                    histology=bool(histology))
                    db.add(patient)
                    db.commit()
                    db.close()
                    
                    flash("Details are saved",'success')
                    return redirect('/results')
                except Exception as e:
                    flash(f'Enter the correct value for numeric fields, {e}', 'danger')
            else:
                flash('enter a valid age', 'danger')
        else:
            flash('enter a valid name','danger')
    return render_template('home.html',title='home')


@app.route('/results')
def result():
    if 'result' in session:
        return render_template('result.html')
    return render_template('home.html')

@app.route('/report')
def reports():
    patients = get_db().query(Patient).all()
    return render_template('report.html', patients=patients)

# create a function to predict the class of a patient
def get_input(age, sex, steriod, antivirals, fatigue, malaise, anorexia, liver_big, liver_firm, spleen_palpable, spiders, ascites, varices, bilirubin, alk_phosphate, sgot, albumin, protime, histology):
    x = {
        "age": age,
        'sex': sex,
        'steroid': steriod,
        'antivirals': antivirals,
        'fatigue': fatigue,
        'malaise': malaise,
        'anorexia': anorexia,
        'liver_big': liver_big,
        'liver_firm': liver_firm,
        'spleen_palable': spleen_palpable,
        'spiders': spiders,
        'ascites': ascites,
        'varices': varices,
        'bilirubin': bilirubin,
        'alk_phosphate': alk_phosphate,
        'sgot': sgot,
        'albumin': albumin,
        'protime': protime,
        'histology': histology
    }
    return x

def predict(xinput):
    xinput = pd.DataFrame(xinput, index=[0])
    print(xinput)
    model = load("Hepatitis/model.joblib")
    y_pred = model.predict(xinput)
    if y_pred == 1:
        return "May have liver disease (Hepatitis)",True
    else:
        return "Don't have liver disease (Hepatitis)" ,False      

@app.route('/about')
def about():
    return render_template('about.html',title='About Us')

@app.route('/logout')
def logout():
    if session.get('isauth'):
        session.clear()
        flash('you have been logged out','warning')
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True,threaded=True)