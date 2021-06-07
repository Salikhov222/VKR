# pylint: disable=no-member
import psycopg2
from datetime import datetime, date
from flask import render_template, flash, redirect, url_for, request, g, session
from app import app
from app.forms import *
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from werkzeug.security import generate_password_hash
import initdb as cn
from app.models import User

cn.createAdmin()

@app.before_request
def before_request():
    g.user = None
    if 'user' in session:
        g.user = session['user']

@app.route('/')
def index():
    return render_template('index.html', title='Home')

@app.route('/about')
def about():
    return render_template('about.html', title='About')


# регистрация
@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = SignUpForm()
    if form.validate_on_submit():
        user = User(login=form.login.data,status=form.status.data, email=form.email.data, phone=form.phone.data)
        user.set_password(form.password.data)
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "INSERT INTO person (login, password, status, email, phone) VALUES (%s, %s, %s, %s, %s);"
        curs.execute(sql, (user.login, user.password, user.status, user.email, user.phone))
        conn.commit()
        conn.close()
        return redirect(url_for('success'))
    return render_template('registration.html', title='Register', form=form)    

# успешная регистрация
@app.route('/success', methods=['GET', 'POST'])
def success():
    return render_template("success.html")

# вход в личный кабинет
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))  # во избежание повторной авторизации
    form = LoginForm()
    if form.validate_on_submit():

        session.pop('user', None)
        username = form.login.data
        password = form.password.data

        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM person WHERE login = %s;"
        curs.execute(sql, (form.login.data,))
        if curs.rowcount == 0:
            return render_template("login.html", message='Пользователя с данным логином не существует!', form=form)
        result = curs.fetchone()
        user_id = result[0]
        status = result[3]  
        conn.commit()
        if username == 'admin' and password == 'admin':
            session['user'] = user_id
            return render_template('admin.html', title='Admin')
        conn.close()
        if result is None:
            user = None
        else:
            user =  User(result['userid'], result['login'], result['password'], result['status'], result['email'], result['phone'])
        if user is None or not user.check_password(form.password.data):
            flash('Неправильные данные для входа!')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        session['user'] = user_id
        return redirect(url_for('profile', status=status, username=username))
    return render_template('login.html', title='Sign In', form=form)
"""         next_page = request.args.get('next')
        if not next_page or url_parse(
                next_page).netloc != '':  # перенаправление на след страницу, если не был авторизован
            next_page = url_for('index')
        return redirect(next_page) """
           
@app.route('/LK')
def LK():
    if current_user.is_authenticated:
        conn = cn.get_connection()
        curs = conn.cursor()
        curs.execute('SELECT * FROM person WHERE login = %s', (current_user.login,))
        result = curs.fetchone()
        status = result[3]
        username = current_user.login
        conn.commit()
        conn.close()
        return redirect(url_for('profile', status=status, username=username))

# выход из личного кабинета
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

#восстановление пароля
@app.route('/passRec', methods=['GET', 'POST'])
def passRec():
    form = PwRecForm()
    if form.validate_on_submit():
        login = form.login.data
        passwordOld = form.passwordOld.data
        passwordNew = form.passwordNew.data
        conn = cn.get_connection()
        curs = conn.cursor()
        curs.execute('SELECT * FROM person WHERE login = %s', (login, ))
        if curs.rowcount == 0:
            return render_template("passRec.html", message='Пользователя с данным логином не существует!', form=form)
        conn.commit()

        if passwordOld != passwordNew:
            return render_template("passRec.html", message='Пароли не совпадают!', form=form)
        passwordHash = generate_password_hash(passwordNew)
        user = User(login=form.login.data)    
        user.set_password(form.passwordNew.data)    
        curs = conn.cursor()
        sql = 'UPDATE person ' \
              'SET password = %s ' \
              'WHERE login = %s;'
        curs.execute(sql,(passwordHash, login))      
        conn.commit()
        conn.close()
        return redirect(url_for('passRecSucc'))
    return render_template("passRec.html", form=form)

# успешное восстановление пароля
@app.route('/passRecSucc', methods=['GET', 'POST'])
def passRecSucc():
    return render_template("passRecSucc.html")


# страница профиля
@app.route('/profile/<status>/<username>', methods=['GET', 'POST'])
def profile(status, username):
    if g.user:
        warning = ''

        if status == 'company':
            inn = cn.loadInfoFromProfile('inn', 'company', username)
            companyName = cn.loadInfoFromProfile('name_firm', 'company', username)
            companyBalance = cn.loadInfoFromProfile('balance', 'company', username)
            companyEmployer_name = cn.loadInfoFromProfile('employer_name', 'company', username)
            companyEmployer_surname = cn.loadInfoFromProfile('employer_surname', 'company', username)
            companyPhone = cn.loadInfoFromPerson('phone', username)
            companyEmail = cn.loadInfoFromPerson('email', username)
            

            if inn == '' or companyName == '':
                warning = True
            return render_template("profile.html", status=status, username=username, inn=inn, companyName=companyName, companyBalance=companyBalance, companyEmployer_name=companyEmployer_name, companyEmployer_surname = companyEmployer_surname, 
                                   companyPhone=companyPhone, companyEmail=companyEmail, warning=warning)

        if status == 'employee':
            fullName = cn.loadInfoFromProfile('fio', 'employee', username)
            sex=cn.loadInfoFromProfile('sex', 'employee', username)
            age=cn.loadInfoFromProfile('age', 'employee', username)
            employeePhone = cn.loadInfoFromPerson('phone', username)
            employeeEmail = cn.loadInfoFromPerson('email', username)
            employeePass = cn.loadInfoFromPerson('password', username)

            if fullName == '':
                warning = True
            return render_template("profile.html", status=status, username=username, fullName=fullName, sex=sex, age=age,
                                   employeePhone=employeePhone, employeeEmail=employeeEmail, employeePass=employeePass, warning=warning)

        if status == 'customer':
            customerName = cn.loadInfoFromProfile('customer_name', 'customer', username)
            customerBalance = cn.loadInfoFromProfile('balance', 'customer', username)
            customerAbout = cn.loadInfoFromProfile('about', 'customer', username)
            customerPhone = cn.loadInfoFromPerson('phone', username)
            customerEmail = cn.loadInfoFromPerson('email', username)

            if customerName == '':
                warning = True
            return render_template("profile.html", status=status, username=username, customerName=customerName, customerBalance=customerBalance, customerAbout=customerAbout,
                                   customerPhone=customerPhone, customerEmail=customerEmail,  warning=warning)

        if status == 'performer':
            performerName = cn.loadInfoFromProfile('performer_name', 'performer', username)
            performerArea = cn.loadInfoFromProfile('area_name', 'performer', username)
            performerAbout = cn.loadInfoFromProfile('about', 'performer', username)
            performerPhone = cn.loadInfoFromPerson('phone', username)
            performerEmail = cn.loadInfoFromPerson('email', username)

            if performerName == '' or performerArea == '' or performerAbout == '':
                warning = True
            return render_template("profile.html", status=status, username=username, performerName=performerName,
                                   performerAbout=performerAbout, performerArea=performerArea, performerPhone=performerPhone,
                                   performerEmail=performerEmail, warning=warning)

    return render_template("profile.html", status=status, username=username)

# страница редактирования профиля
@app.route('/profile_edit/<status>/<username>', methods=['GET', 'POST'])
def profile_edit(status, username):
    userID = cn.getUserID(username)
    conn = cn.get_connection2()
    cur = conn.cursor()
    warning = True

    cur.execute('SELECT email, phone, password FROM person WHERE userid = %s', (userID,))
    result = cur.fetchall()
    contacts = []
    if result:
        contacts = list(sum(result, ()))
    conn.commit()

    cur.execute('SELECT inn, name_firm, balance, employer_name, employer_surname FROM company WHERE userid = %s', (userID,))
    result = cur.fetchall()
    companyInfo = []
    if result:
        companyInfo = list(sum(result, ()))
    conn.commit()

    cur.execute('SELECT fio, sex, age FROM employee WHERE userid = %s', (userID,))
    result = cur.fetchall()
    employeeInfo = []
    if result:
        employeeInfo = list(sum(result, ()))
    conn.commit()

    cur.execute('SELECT customer_name, balance, about FROM customer WHERE userid = %s', (userID,))
    result = cur.fetchall()
    customerInfo = []
    if result:
        customerInfo = list(sum(result, ()))
    conn.commit()

    cur.execute('SELECT performer_name, area_name, about FROM performer WHERE userid = %s', (userID,))
    result = cur.fetchall()
    performerInfo = []
    if result:
        performerInfo = list(sum(result, ()))
    conn.commit()

    if companyInfo:
        formCompany = ProfEdCompanyForm(inn=companyInfo[0], companyName=companyInfo[1], companyBalance=companyInfo[2], companyEmloyer_name=companyInfo[3], 
                                        companyEmloyer_surname=companyInfo[4], companyEmail=contacts[0], companyPhone=contacts[1])
    else:
        formCompany = ProfEdCompanyForm(companyEmail=contacts[0], companyPhone=contacts[1])

    # formCompany.UpInd()

    if employeeInfo:
        formEmployee = ProfEdEmployeeForm(fullName=employeeInfo[0], sex=employeeInfo[1], age=employeeInfo[2], employeeEmail=contacts[0], employeePhone=contacts[1])
    else:
        formEmployee = ProfEdEmployeeForm(employeeEmail=contacts[0], employeePhone=contacts[1])   

    if customerInfo:
        formCustomer = ProfEdCustomerForm(customerName=customerInfo[0], balance=customerInfo[1], about=customerInfo[2], customerEmail=contacts[0], customerPhone=contacts[1])
    else:
        formCustomer = ProfEdCustomerForm(customerEmail=contacts[0], customerPhone=contacts[1])   

    if performerInfo:
        formPerformer = ProfEdPerformerForm(performerName=performerInfo[0], performerArea=performerInfo[1], performerAbout=performerInfo[2], performerEmail=contacts[0], performerPhone=contacts[1])
    else:
        formPerformer = ProfEdPerformerForm(performerEmail=contacts[0], performerPhone=contacts[1])   
    formPerformer.UpArea()

    if g.user:
        if status == 'company' and formCompany.validate_on_submit():
            inn = formCompany.inn.data
            companyName = formCompany.companyName.data
            companyBalance = formCompany.companyBalance.data
            companyEmployer_name = formCompany.companyEmployer_name.data
            companyEmployer_surname = formCompany.companyEmployer_surname.data 
            companyPhone = formCompany.companyPhone.data
            companyEmail = formCompany.companyEmail.data

            isCompany = userExist('company', userID)     
            try:
                if isCompany == 0:
                    if inn == '' or companyName == ''  or companyEmployer_name == '' or companyEmployer_surname == '':
                        return render_template("profile_edit.html", message='Пожайлуста, введите ИНН, название компании, а также Имя и Фамилию работодателя', status=status, username=username, formCompany=formCompany, warning=warning)
                    cur.execute("insert into company (userid, inn, name_firm, balance, employer_name, employer_surname) values (%s, %s, %s, %s, %s, %s)",
                                (userID, inn, companyName, companyBalance, companyEmployer_name, companyEmployer_surname,))
                else:
                    if inn != '':
                        cur.execute('update company set inn = %s WHERE userid = %s', (inn, userID,))
                    if companyName != '':
                        cur.execute('update company set name_firm = %s WHERE userid = %s', (companyName, userID,))  
                    if companyEmployer_name != '':
                        cur.execute('update company set employer_name = %s WHERE userid = %s', (companyEmployer_name, userID,))    
                    if companyEmployer_surname != '':
                        cur.execute('update company set employer_surname = %s WHERE userid = %s', (companyEmployer_surname, userID,))    
                    if companyPhone != '':
                        cur.execute('update person set phone = %s WHERE userid = %s', (companyPhone, userID,))
                    if companyEmail != '':
                        cur.execute('update person set email = %s WHERE userid = %s', (companyEmail, userID,))            
                conn.commit()
            except psycopg2.Error:
                conn.rollback()
                return render_template("profile_edit.html",
                                       message='Пользователь с данным ИНН, телефоном или email уже существует! Или проверьте правильность ввода ИНН, он не должен превышать 12 символов',
                                       status=status, username=username, formCompany=formCompany, warning=warning)   
            return redirect(url_for('profile', status=status, username=username))

        if status == 'employee' and formEmployee.validate_on_submit():
            fullName = formEmployee.fullName.data
            sex = formEmployee.sex.data
            age = formEmployee.age.data
            employeePhone = formEmployee.employeePhone.data
            employeeEmail = formEmployee.employeeEmail.data

            isEmployee = cn.userExist('employee', userID)

            try:
                if isEmployee == 0:
                    if fullName == '' or sex == '' or age == '':
                        return render_template("profile_edit.html", message='Пожайлуста, введите ФИО, Ваш пол и возраст', status=status, username=username, formEmployee=formEmployee, warning=warning)
                    cur.execute("INSERT INTO employee (userid, fio, sex, age) VALUES (%s, %s, %s, %s)", (userID, fullName, sex, age,))
                else:
                    if fullName != '':
                        cur.execute('update employee set fio = %s WHERE userid = %s', (fullName, userID, ))
                    if sex != '':
                        cur.execute('update employee set sex = %s WHERE userid = %s', (sex, userID, ))    
                    if age != '':
                        cur.execute('update employee set age = %s WHERE userid = %s', (age, userID, ))    
                    if employeePhone != '':
                        cur.execute('update person set phone = %s WHERE userid = %s', (employeePhone, userID,))
                    if employeeEmail != '':
                        cur.execute('update person set email = %s WHERE userid = %s', (employeeEmail, userID,))
                conn.commit()
            except psycopg2.Error:
                conn.rollback()
                return render_template("profile_edit.html", message='Пользователь с данным телефоном или email уже существует!', status=status, username=username, formEmployee=formEmployee, warning=warning)
            return redirect(url_for('profile', status=status, username=username))
        
        if status == 'customer' and formCustomer.validate_on_submit():
            customerName = formCustomer.customerName.data
            balance = formCustomer.customerBalance.data
            about = formCustomer.customerAbout.data
            customerPhone = formCustomer.customerPhone.data
            customerEmail = formCustomer.customerEmail.data

            isCustomer = cn.userExist('customer', userID)

            try:
                if isCustomer == 0:
                    if customerName == '':
                        return render_template("profile_edit.html", message='Пожайлуста, введите Ваше Имя', status=status, username=username, formCustomer=formCustomer, warning=warning)
                    cur.execute("INSERT INTO customer (userid, customer_name, balance, about) VALUES (%s, %s, %s, %s)", (userID, customerName, balance, about,))
                else:
                    if customerName != '':
                        cur.execute('update customer set customer_name = %s WHERE userid = %s', (customerName, userID, ))
                    if balance != '':
                        cur.execute('update customer set balance = %s WHERE userid = %s', (balance, userID, ))    
                    if about != '':
                        cur.execute('update customer set about = %s WHERE userid = %s', (about, userID, ))    
                    if customerPhone != '':
                        cur.execute('update person set phone = %s WHERE userid = %s', (customerPhone, userID,))
                    if customerEmail != '':
                        cur.execute('update person set email = %s WHERE userid = %s', (customerEmail, userID,))
                conn.commit()
            except psycopg2.Error:
                conn.rollback()
                return render_template("profile_edit.html", message='Пользователь с данным телефоном или email уже существует!', status=status, username=username, formCustomer=formCustomer, warning=warning)
            return redirect(url_for('profile', status=status, username=username))

        if status == 'performer' and formPerformer.validate_on_submit():
            performerName = formPerformer.performerName.data
            performerArea = formPerformer.performerArea.data
            performerAbout = formPerformer.performerAbout.data
            performerPhone = formPerformer.performerPhone.data
            performerEmail = formPerformer.performerEmail.data

            isPerformer = userExist('performer', userID)

            try:
                if isPerformer == 0:
                    if performerName == '' or performerArea == '' or performerAbout == '':
                        return render_template("profile_edit.html", message='Пожайлуста, введите Ваше имя, сферу деятельности и описание услуг', status=status, username=username, formPerformer=formPerformer, warning=warning)
                    cur.execute("INSERT INTO performer (userid, performer_name, area_name, about) values (%s, %s, %s, %s)", (userID, performerName, performerArea, performerAbout, ))
                else:
                    if performerName != '':
                        cur.execute('update performer set performer_name = %s WHERE userid = %s', (performerName, userID, ))
                    if performerArea != '':
                        cur.execute('update performer set area_name = %s WHERE userid = %s', (performerArea, userID, ))
                    if performerAbout != '':
                        cur.execute('update performer set about = %s WHERE userid = %s', (performerAbout, userID, ))
                    if performerPhone != '':
                        cur.execute('update person set phone = %s WHERE userid = %s', (performerPhone, userID,))
                    if performerEmail != '':
                        cur.execute('update person set email = %s WHERE userid = %s', (performerEmail, userID,))
                conn.commit()
            except psycopg2.Error:
                conn.rollback()
                return render_template("profile_edit.html", message='Пользователь с данным телефоном или email уже существует!', status=status, username=username, formPerformer=formPerformer, warning=warning)
            return redirect(url_for('profile', status=status, username=username))

        #return render_template("profile_edit.html", status=status, username=username, formCompany=formCompany, formEmployee=formEmployee) 
    warning = True
    return render_template("profile_edit.html", status=status, username=username, formCompany=formCompany, formEmployee=formEmployee, formPerformer=formPerformer, formCustomer=formCustomer, warning=warning)
    
#изменение пароля    
@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.check_password(form.old_password.data):
            conn = cn.get_connection()
            curs = conn.cursor()
            curs.execute('SELECT * FROM person WHERE login = %s', (current_user.login,))
            result = curs.fetchone()
            status = result[3]
            username = current_user.login
            sql = 'UPDATE person ' \
                  'SET password = %s' \
                  'WHERE login = %s;'
            current_user.set_password(form.new_password.data)
            curs.execute(sql, (current_user.password, current_user.login,))
            conn.commit()
            conn.close()
            return redirect(url_for('profile', status=status, username=username))
        else:
            flash('Wrong password. Please check again')
    return render_template('change_password.html', title='Change Password', form=form)

#пополнение баланса
@app.route('/balance/<status>/<username>', methods=['GET', 'POST'])
def balance(status, username):
    form = BalanceForm()
    userID = getUserID(username)
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        balanceComp = form.balance.data
        try:
            curs.execute('update company set balance = balance + %s WHERE userid = %s', (balanceComp, userID))
            conn.commit()
            conn.close()
        except psycopg2.Error:
            con.rollback()
            return render_template('popolnenie.html', message = "Проверьте правильность ввода!", form=form, status=status, username=username)
        return redirect(url_for('profile', status=status, username=username))
    return render_template('popolnenie.html', form=form, status=status, username=username)    

#пополнение баланса
@app.route('/balanceCust/<status>/<username>', methods=['GET', 'POST'])
def balanceCust(status, username):
    form = BalanceForm()
    userID = getUserID(username)
    if form.validate_on_submit():
        conn = cn.get_connection()
        curs = conn.cursor()
        balanceCust = form.balance.data
        try:
            curs.execute('update customer set balance = balance + %s WHERE userid = %s', (balanceCust, userID))
            conn.commit()
            conn.close()
        except psycopg2.Error:
            con.rollback()
            return render_template('popolnenieCust.html', message = "Проверьте правильность ввода!", form=form, status=status, username=username)
        return redirect(url_for('profile', status=status, username=username))
    return render_template('popolnenieCust.html', form=form, status=status, username=username)  

# просмотры
@app.route('/views/<status>/<username>/<itemid>')
def prosmotri(status, username, itemid):
    conn = cn.get_connection2()
    curs = conn.cursor()
    
    curs.execute("SELECT name_firm, date_view FROM company NATURAL JOIN view_summary WHERE number_s = %s", (itemid,))
    viewsInfo = curs.fetchall()
    conn.commit()
    conn.close()
    
    return render_template("views.html", status=status, username=username, viewsInfo=viewsInfo)

# просмотр откликов
@app.route('/views_otkliki/<status>/<username>/<itemid>')
def ViewOtkliki(status, username, itemid):
    conn = cn.get_connection2()
    curs = conn.cursor()
    
    curs.execute("SELECT date_otklik, fio, sex, age FROM employee NATURAL JOIN otkliki WHERE number_v = %s", (itemid,))
    viewsInfo = curs.fetchall()
    conn.commit()
    conn.close()
    
    return render_template("otklik.html", status=status, username=username, viewsInfo=viewsInfo)

# просмотр заявок
@app.route('/views_request/<status>/<username>/<itemid>')
def ViewRequest(status, username, itemid):
    conn = cn.get_connection2()
    curs = conn.cursor()
    
    curs.execute("SELECT date_req, performer_name, about FROM performer NATURAL JOIN request WHERE task_id = %s", (itemid,))
    viewsInfo = curs.fetchall()
    conn.commit()
    conn.close()
    
    return render_template("request.html", status=status, username=username, viewsInfo=viewsInfo)

#добавление записи
@app.route('/create_item/<status>/<username>', methods=['GET', 'POST'])
def createItem(status, username):
    formCompany = CreateItemCompanyForm()
    formEmployee = CreateItemEmployeeForm()
    formCustomer = CreateItemCustomerForm()
    formCustomer.UpArea()
    formCompany.UpInd()
    formCompany.UpProf()
    formEmployee.UpInd()
    formEmployee.UpProf()   

    if g.user:
        userID = getUserID(username)

        if status == 'company' and formCompany.validate_on_submit():
            industryName = formCompany.industryName.data
            professionName = formCompany.professionName.data
            about = formCompany.about.data
            minSalary = formCompany.minSalary.data
            maxSalary = formCompany.maxSalary.data
            minExp = formCompany.minExp.data
            conditions = formCompany.conditions.data
            requirements = formCompany.requirements.data
            duties = formCompany.duties.data
            empType = formCompany.empType.data

            vacPubData = date.today()

            if minExp == 0:
                minExp = 'Без опыта'
            cur.execute('SELECT * FROM post_industry WHERE industry_name = %s and post_name = %s', (industryName, professionName,))
            result = cur.fetchone()
            if result is None:
                return render_template("create_item.html", message='Выбранная должность не соответствует выбранной отрасли!', status=status,
                                       username=username, formCompany=formCompany)
            
            try:
                cur.execute(
                    "insert into vacancy (userid, industry_name, post, about, salary_from, salary_to, exp_from, conditions, requirements, duties, schedule, date_vac) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s)",
                    (userID, industryName, professionName, about, minSalary,
                     maxSalary, minExp, conditions, requirements, duties, empType, vacPubData ))        
                cur.execute('update company set balance = balance - 2500 WHERE userid = %s', (userID,))     
                con.commit()
            except psycopg2.Error:
                con.rollback()
                return render_template("create_item.html", message='Проверьте правильность введенных данных! Или на вашем счету недостаточно средств для публикации вакансии!', status=status, username=username, formCompany=formCompany)
            return redirect(url_for('itemList', status=status, username=username))  

        if status == 'employee' and formEmployee.validate_on_submit():
            industryName = formEmployee.industryName.data
            professionName = formEmployee.professionName.data
            minSalary = formEmployee.minSalary.data
            maxSalary = formEmployee.maxSalary.data
            exp = formEmployee.exp.data
            edType = formEmployee.edType.data
            edInst = formEmployee.edInst.data
            skills = formEmployee.skills.data
            empType = formEmployee.empType.data
           

            cvPubData = date.today()

            if minSalary == '':
                minSalary = None
            elif maxSalary == '':
                maxSalary = None
            if exp == 0:
                exp = 'Без опыта'
        
            cur.execute('SELECT * FROM post_industry WHERE industry_name = %s and post_name = %s', (industryName, professionName,))
            result = cur.fetchone()
            if result is None:
                return render_template("create_item.html", message='Выбранная должность не соответствует выбранной отрасли!', status=status,
                                       username=username, formEmployee=formEmployee)

            try:
                cur.execute(
                "insert into summary (userid, industry_name, post, salary_from, salary_to, experience, edtype, edinst, skills, schedule, date_summ) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (userID, industryName, professionName, minSalary, maxSalary, exp, edType, edInst, skills, empType, cvPubData ))
                con.commit()
            except psycopg2.Error:
                con.rollback()
                return render_template("create_item.html", message='Проверьте правильность введенных данных!', status=status, username=username, formEmployee=formEmployee)
            return redirect(url_for('itemList', status=status, username=username))  

        if status == 'customer' and formCustomer.validate_on_submit():
            areaName = formCustomer.areaName.data
            taskAbout = formCustomer.taskAbout.data
            dateInput = formCustomer.dateInput.data
            price = formCustomer.price.data


            today = date.today()

            if dateInput < today:
                return render_template("create_item.html", message='Дата выполнения не может быть раньше сегодняшней',
                                       status=status, username=username, formCustomer=formCustomer)

            try:
                cur.execute(
                "insert into task (userid, area_name, about_task, date_task, cost) values (%s, %s, %s, %s, %s)",
                (userID, areaName, taskAbout, dateInput, price))
                cur.execute('select cost from task where userid = %s', (userID,))
                result = cur.fetchone()
                cost = result
                cur.execute('update customer set balance = (balance - %s*0.05 - %s) WHERE userid = %s', (result, cost, userID,))
                con.commit()
            except psycopg2.Error:
                con.rollback()
                return render_template("create_item.html", message='В численные поля записан текст!',
                                       status=status, username=username, formCustomer=formCustomer)
            return redirect(url_for('itemList', status=status, username=username))


    return render_template("create_item.html", status=status, username=username, formCompany=formCompany, formEmployee=formEmployee, formCustomer=formCustomer)

#список записей
@app.route('/item_list/<status>/<username>')
def itemList(status, username):
    conn = cn.get_connection2()
    cur = conn.cursor()
    if g.user:
        viewsCount = []
        viewsCount2 = []
        viewsCount3 = []

        userID = getUserID(username)

        cur.execute('SELECT number_v, industry_name, post, about, salary_from, salary_to, exp_from, conditions, requirements, duties, schedule, date_vac FROM vacancy WHERE userid = %s', (userID,))
        vacancyInfo = cur.fetchall()
        vacancyInfo = [list(elem) for elem in vacancyInfo]
        conn.commit()

        cur.execute('SELECT number_s, industry_name, post, salary_from, salary_to, experience, edtype, edinst, skills, schedule, date_summ, rating FROM summary WHERE userid = %s', (userID,))
        cvInfo = cur.fetchall()
        cvInfo = [list(elem) for elem in cvInfo]
        conn.commit()   

        cur.execute('SELECT task_id, area_name, about_task, date_task, cost FROM task WHERE userid = %s', (userID,))
        taskInfo = cur.fetchall()
        taskInfo = [list(elem) for elem in taskInfo]
        conn.commit()

        cur.execute('SELECT number_s FROM summary WHERE userid = %s', (userID,))
        cvIDs = cur.fetchall()
        cvIDs = list(sum(cvIDs, ()))
        conn.commit()

        cur.execute('SELECT number_v FROM vacancy WHERE userid = %s', (userID,))
        vacIDs = cur.fetchall()
        vacIDs = list(sum(vacIDs, ()))
        conn.commit()

        cur.execute('SELECT task_id FROM task WHERE userid = %s', (userID,))
        taskIDs = cur.fetchall()
        taskIDs = list(sum(taskIDs, ()))
        conn.commit()

        for item in cvIDs:
            cur.execute('SELECT count(*) FROM view_summary WHERE number_s = (select number_s from summary where number_s = %s)', (item,))
            result = cur.fetchone()
            viewsCount.append(result[0])
            conn.commit()

        for item in vacIDs:
            cur.execute('SELECT count(*) FROM otkliki WHERE number_v = (select number_v from vacancy where number_v = %s)', (item,))
            result = cur.fetchone()
            viewsCount2.append(result[0])
            conn.commit()        

        for item in taskIDs:
            cur.execute('SELECT count(*) FROM request WHERE task_id = (select task_id from task where task_id = %s)', (item,))
            result = cur.fetchone()
            viewsCount3.append(result[0])
            conn.commit()   

        for f, b in list(zip(cvInfo, viewsCount)):
            f.append(b)
        for z, c in list(zip(vacancyInfo, viewsCount2)):
            z.append(c)
        for p, d in list(zip(taskInfo, viewsCount3)):
            p.append(d)


    return render_template("item_list.html", status=status, username=username, vacancyInfo=vacancyInfo, cvInfo=cvInfo, taskInfo=taskInfo)

# изменение записи
@app.route('/edititem/<status>/<username>/<itemid>', methods=['GET', 'POST'])
def editItem(status, username, itemid):
    conn = cn.get_connection2()
    cur = conn.cursor()
    formCompany = []
    formEmployee = []
    formCustomer = []

    if g.user:
        if status == 'company':
            cur.execute(
                'SELECT industry_name, post, about, salary_from, salary_to, exp_from, conditions, requirements, duties, schedule FROM vacancy WHERE number_v = %s',
                (itemid,))
            vacancyInfo = cur.fetchall()
            vacancyInfo = list(sum(vacancyInfo, ()))
            conn.commit()

            for i in range(len(vacancyInfo)):
                if vacancyInfo[i] is None:
                    vacancyInfo[i] = ''
            if vacancyInfo[5] == 'без опыта':
                vacancyInfo[5] = 0

            formCompany = CreateItemCompanyForm(industryName=vacancyInfo[0], professionName=vacancyInfo[1],
                                                about=vacancyInfo[2], salary_from=vacancyInfo[3],
                                                salary_to=vacancyInfo[4], exp_from=vacancyInfo[5],
                                                conditions=vacancyInfo[6], requirements=vacancyInfo[7],
                                                duties=vacancyInfo[8], schedule=vacancyInfo[9])
            formCompany.UpInd()
            formCompany.UpProf()
     
            if formCompany.validate_on_submit():
                industryName = formCompany.industryName.data
                professionName = formCompany.professionName.data
                about = formCompany.about.data
                minSalary = formCompany.minSalary.data
                maxSalary = formCompany.maxSalary.data
                minExp = formCompany.minExp.data
                conditions = formCompany.conditions.data
                requirements = formCompany.requirements.data 
                duties = formCompany.duties.data
                empType = formCompany.empType.data


                if minExp == 0:
                    minExp = 'Без опыта'
                cur.execute('SELECT * FROM post_industry WHERE industry_name = %s and post_name = %s', (industryName, professionName,))
                result = cur.fetchone()
                if result is None:
                    return render_template("edit_item.html", message='Выбранная должность не соответствует выбранной отрасли!', status=status,
                                       username=username, formCompany=formCompany)
                try:
                    if industryName != None:
                        cur.execute('update vacancy set industry_name = %s WHERE number_v = %s', (industryName, itemid,))
                    if professionName != None:
                        cur.execute('update vacancy set post = %s WHERE number_v = %s', (professionName, itemid,))
                    if about != None:
                        cur.execute('update vacancy set about = %s WHERE number_v = %s', (about, itemid,))
                    if minSalary != '':
                        cur.execute('update vacancy set salary_from = %s WHERE number_v = %s', (minSalary, itemid,))
                    if maxSalary != '':
                        cur.execute('update vacancy set salary_to = %s WHERE number_v = %s', (maxSalary, itemid,))
                    if minExp != '':
                        cur.execute('update vacancy set exp_from = %s WHERE number_v = %s', (minExp, itemid,))
                    if conditions != '':
                        cur.execute('update vacancy set conditions = %s WHERE number_v = %s', (conditions, itemid,))
                    if requirements != None:
                        cur.execute('update vacancy set requirements = %s WHERE number_v = %s', (requirements, itemid,))
                    if duties != None:
                        cur.execute('update vacancy set duties = %s WHERE number_v = %s', (duties, itemid,))    
                    if empType != None:
                        cur.execute('update vacancy set schedule = %s WHERE number_v = %s', (empType, itemid,))    
                    conn.commit()
                except psycopg2.Error:
                    conn.rollback()
                    return render_template("edit_item.html", message='Проверьте правильность введенных данных!', status=status, username=username, itemid=itemid, formCompany=formCompany)   
                return redirect(url_for('itemList', status=status, username=username))

        if status == 'employee':
            cur.execute(
                'SELECT industry_name, post, salary_from, salary_to, experience, edtype, edinst, skills, schedule FROM summary WHERE number_s = %s',
                (itemid,))
            cvInfo = cur.fetchall()
            cvInfo = list(sum(cvInfo, ()))
            conn.commit()

            for i in range(len(cvInfo)):
                if cvInfo[i] is None:
                    cvInfo[i] = ''
            if cvInfo[4] == 'Без опыта':
                cvInfo[4] = 0

            formEmployee = CreateItemEmployeeForm(industryName=cvInfo[0], professionName=cvInfo[1], minSalary=cvInfo[2],
                                                  maxSalary=cvInfo[3], exp=cvInfo[4], edType=cvInfo[5], edInst=cvInfo[6], skills=cvInfo[7], empType=cvInfo[8]) 

            formEmployee.UpInd()
            formEmployee.UpProf()

            if formEmployee.validate_on_submit():
                industryName = formEmployee.industryName.data
                professionName = formEmployee.professionName.data
                minSalary = formEmployee.minSalary.data
                maxSalary = formEmployee.maxSalary.data
                exp = formEmployee.exp.data
                edType = formEmployee.edType.data
                edInst = formEmployee.edInst.data
                skills = formEmployee.skills.data
                empType = formEmployee.empType.data
                

                if minSalary == '':
                    minSalary = None
                elif maxSalary == '':
                    maxSalary = None
                if exp == 0:
                    exp = 'Без опыта'

                cur.execute('SELECT * FROM post_industry WHERE industry_name = %s and post_name = %s', (industryName, professionName,))
                result = cur.fetchone()
                if result is None:
                    return render_template("edit_item.html",
                                       message='Выбранная должность не соответствует выбранной отрасли!', status=status,
                                       username=username, formEmployee=formEmployee)
                if industryName != None:
                    cur.execute('update summary set industry_name = %s WHERE number_s = %s', (industryName, itemid,))
                if professionName != None:
                    cur.execute('update summary set post = %s WHERE number_s = %s', (professionName, itemid,))
                if minSalary != '':
                    cur.execute('update summary set salary_from = %s WHERE number_s = %s', (minSalary, itemid,))
                if maxSalary != '':
                    cur.execute('update summary set salary_to = %s WHERE number_s = %s', (maxSalary, itemid,))
                if exp != '':
                    cur.execute('update summary set experience = %s WHERE number_s = %s', (exp, itemid,))
                if edType != '':
                    cur.execute('update summary set edType = %s WHERE number_s = %s', (edType, itemid,))  
                if edInst != '':
                    cur.execute('update summary set edInst = %s WHERE number_s = %s', (edInst, itemid,)) 
                if skills != '':
                    cur.execute('update summary set skills = %s WHERE number_s = %s', (skills, itemid,))           
                if empType != None:
                    cur.execute('update summary set schedule = %s WHERE number_s = %s', (empType, itemid,))
                conn.commit() 
                return redirect(url_for('itemList', status=status, username=username))

        if status == 'customer':
            cur.execute('SELECT area_name, about_task, date_task, cost FROM task WHERE task_id = %s', (itemid,))
            taskInfo = cur.fetchall()
            taskInfo = list(sum(taskInfo, ()))
            conn.commit()

            datetime_obj = datetime.strptime(taskInfo[2], "%Y-%m-%d")
            taskInfo[2] = datetime_obj.date()

            formCustomer = CreateItemCustomerForm(areaName=taskInfo[0], taskAbout=taskInfo[1], dateInput=taskInfo[2], price=taskInfo[3])

            if formCustomer.validate_on_submit():
                areaName = formCustomer.areaName.data
                taskAbout = formCustomer.taskAbout.data
                dateInput = formCustomer.dateInput.data
                price = formCustomer.price.data

                today = date.today()

                if areaName != None:
                    cur.execute('update task set area_name = %s WHERE task_id = %s', (areaName, itemid,))
                if taskAbout != '':
                    cur.execute('update task set about_task = %s WHERE task_id = %s', (taskAbout, itemid,))
                if dateInput != '':
                    if dateInput < today:
                        return render_template("edit_item.html",
                                               message='Дата выполнения не может быть раньше сегодняшней',
                                               status=status, username=username, formCustomer=formCustomer)
                    cur.execute('update task set date_task = %s WHERE task_id = %s', (dateInput, itemid,))
                if price != '':
                    cur.execute('update task set cost = %s WHERE task_id = %s', (price, itemid,))
                conn.commit()
                return redirect(url_for('itemList', status=status, username=username))
 
    return render_template("edit_item.html", status=status, username=username, itemid=itemid, formCompany=formCompany, formEmployee=formEmployee, formCustomer=formCustomer)

# удаление записи
@app.route('/deleteitem/<status>/<username>/<itemid>', methods=['POST'])
def deleteItem(status, username, itemid):
    conn = cn.get_connection()
    cur = conn.cursor()
    if g.user:
        if status == 'company':
            cur.execute('delete from vacancy where number_v = %s', (itemid,))
            conn.commit()

        if status == 'employee':
            cur.execute('delete from summary where number_s = %s', (itemid,))
            conn.commit()

        if status == 'customer':
            cur.execute('delete from task where task_id = %s', (itemid,))
            conn.commit()

            conn.close()
    return redirect(url_for('itemList', status=status, username=username))

# КАТАЛОГ РЕЗЮМЕ
# отрасли
@app.route('/summ_cat_ind/<status>/<username>')
def summCatInd(username, status):
    conn = get_connection2()
    cur = conn.cursor()

    counts = []
    industriesURL = []

    cur.execute('SELECT industry_name FROM post_industry WHERE industry_name in (select industry_name from summary) group by industry_name')
    industries = cur.fetchall() 
    conn.commit()

    industries = list(sum(industries, ()))

    for item in industries:
        cur.execute('SELECT count(*) FROM summary WHERE industry_name = %s', (item,))
        count = cur.fetchone()
        counts.append(count)
        conn.commit()

    counts = list(sum(counts, ()))

    for item in industries:
        itemUni = translitToURL(item)
        industriesURL.append(itemUni)

    data = list(zip(industries, counts, industriesURL))
    return render_template("summ_cat_ind.html", username=username, data=data, status=status)

# должности
@app.route('/summ_cat_pro/<status>/<username>/<industryURL>')
def summCatPro(status, username, industryURL):
    conn = get_connection2()
    cur = conn.cursor()

    counts = []
    professionsURL = []
    industry = industryURL

    cur.execute('SELECT post_name FROM post_industry WHERE post_name in (select post from summary where industry_name = %s)', (industry,))
    professions = cur.fetchall()
    conn.commit()

    professions = list(sum(professions, ()))

    for item in professions:
        cur.execute('SELECT count(*) FROM summary WHERE post = %s', (item,))
        count = cur.fetchone()
        counts.append(count)
        conn.commit()
            

    counts = list(sum(counts, ()))

    for item in professions:
        itemUni = translitToURL(item)
        professionsURL.append(itemUni)

    data = list(zip(professions, counts, professionsURL))
    return render_template("summ_cat_pro.html", username=username, data=data, industryURL=industryURL, status=status)

# список резюме
@app.route('/summ_cat_list/<status>/<username>/<industryURL>/<professionURL>', methods=['GET', 'POST'])
def summCatList(username, industryURL, professionURL, status):
    conn = get_connection()
    cur = conn.cursor()
    userID = getUserID(username)
    industry = industryURL
    profession = professionURL

    formRating = RatingResume()

    cur.execute('SELECT number_s, industry_name, post, salary_from, salary_to, experience, edtype, edinst, skills, schedule, date_summ FROM summary WHERE industry_name = %s and post = %s', (industry, profession))
    cvInfo = cur.fetchall()
    conn.commit()

    if g.user:
        cur.execute('SELECT number_s, industry_name, post, salary_from, salary_to, experience, edtype, edinst, skills, schedule, date_summ FROM summary WHERE industry_name = %s and post = %s', (industry, profession))
        cvInfo = cur.fetchall()
        conn.commit()
        cur.execute('SELECT number_s FROM summary WHERE industry_name = %s and post = %s', (industry, profession))
        result = cur.fetchone()
        numS = result[0]
        conn.commit()

        if formRating.validate_on_submit():
            rating = formRating.rating.data
            
            try:
                cur.execute('UPDATE summary set rating = %s WHERE number_s = %s', (rating, numS))
                conn.commit()
            except psycopg2.Error:
                conn.rollback()
                return render_template("summ_cat_list.html", message = 'Оценка не поставлена', username=username, cvInfo=cvInfo,  industryURL=industryURL, professionURL=professionURL, status=status, formRating=formRating)
            return render_template("summ_cat_list.html", message = 'Оценка поставлена', username=username, cvInfo=cvInfo,  industryURL=industryURL, professionURL=professionURL, status=status, formRating=formRating)    
    return render_template("summ_cat_list.html", username=username, cvInfo=cvInfo, userid = userID,  industryURL=industryURL, professionURL=professionURL, status=status, formRating=formRating)

# резюме полностью
@app.route('/summ_cat_item/<status>/<username>/<industryURL>/<professionURL>/<userid>/<itemid>', methods=['GET', 'POST'])
def summCatItem(userid, itemid, industryURL, professionURL, status, username):
    conn = get_connection2()
    cur = conn.cursor()
    userID = getUserID(username)
    if g.user:
        data = date.today()
        pay = '1'

        cur.execute("insert into view_summary (userid, number_s, date_view, payment) values (%s, %s, %s, %s)", (userid, itemid, data, pay))
        conn.commit()

        cur.execute('SELECT * FROM summary WHERE number_s = %s', (itemid,))
        result = cur.fetchall()
        cvInfo = list(sum(result, ()))
        conn.commit()

        cur.execute('SELECT fio FROM employee WHERE userid = (select userid from summary where number_s = %s)', (itemid,))
        result = cur.fetchone()
        fullName = result[0]
        conn.commit()

        cur.execute('SELECT email, phone FROM person WHERE userid = (select userid from summary where number_s = %s)', (itemid,))
        result = cur.fetchall()
        contacts = list(sum(result , ()))
        conn.commit()
        try:
            cur.execute('update company set balance = balance - 1500 WHERE userid = %s', (userID,))
            conn.commit()
            conn.close()
        except psycopg2.Error:
            conn.rollback()
            return render_template("net_sredstv.html", message = 'На вашем счету недостаточно средств для просмотра контактных данных!', status=status, username=username)
        return render_template("summ_cat_item.html", itemid=itemid, userid=userid, cvInfo=cvInfo, fullName=fullName, contacts=contacts, status=status, username=username, industryURL=industryURL, professionURL=professionURL)
    return render_template("summ_cat_item.html", itemid=itemid, userid=userid, cvInfo=cvInfo, fullName=fullName, contacts=contacts, status=status, username=username, industryURL=industryURL, professionURL=professionURL)

# КАТАЛОГ ВАКАНСИЙ
# отрасли
@app.route('/vacancy_cat_ind/<status>/<username>')
def vacCatInd(status, username):
    conn = get_connection2()
    cur = conn.cursor()
    counts = []
    industriesURL = []

    cur.execute('SELECT industry_name FROM post_industry WHERE industry_name in (select industry_name from vacancy) group by industry_name')
    industries = cur.fetchall()
    conn.commit()

    industries = list(sum(industries, ()))

    for item in industries:
        cur.execute('SELECT count(*) FROM vacancy WHERE industry_name = %s', (item,))
        count = cur.fetchone()
        counts.append(count)
        conn.commit()

    counts = list(sum(counts, ()))

    for item in industries:
        itemUni = translitToURL(item)
        industriesURL.append(itemUni)

    data = list(zip(industries, counts, industriesURL))
    return render_template("vacancy_cat_ind.html", data=data, username=username, status=status)

# должности
@app.route('/vacancy_cat_pro/<status>/<username>/<industryURL>')
def vacCatPro(status, username, industryURL):
    conn = get_connection2()
    cur = conn.cursor()
    counts = []
    professionsURL = []
    industry = industryURL

    cur.execute('SELECT post_name FROM post_industry WHERE post_name in (select post from vacancy where industry_name = %s)', (industry,))
    professions = cur.fetchall()
    conn.commit()

    professions = list(sum(professions, ()))

    for item in professions:
        cur.execute('SELECT count(*) FROM vacancy WHERE post = %s', (item,))
        count = cur.fetchone()
        counts.append(count)
        conn.commit()
        conn.close()

    counts = list(sum(counts, ()))

    for item in professions:
        itemUni = translitToURL(item)
        professionsURL.append(itemUni)

    data = list(zip(professions, counts, professionsURL))
    return render_template("vacancy_cat_pro.html", data=data, industryURL=industryURL, status=status, username=username)

# список вакансий
@app.route('/vacancy_cat_list/<status>/<username>/<industryURL>/<professionURL>')
def vacCatList(status, username, industryURL, professionURL):
    conn = get_connection()
    cur = conn.cursor() 
    industry = industryURL
    profession = professionURL

    cur.execute('SELECT number_v, industry_name, post, about, salary_from, salary_to, exp_from, conditions, requirements, duties, schedule, date_vac FROM vacancy WHERE industry_name = %s and post = %s', (industry, profession))
    vacancyInfo = cur.fetchall()
    conn.commit()
    return render_template("vacancy_cat_list.html", vacancyInfo=vacancyInfo, industryURL=industryURL, professionURL=professionURL, status=status, username=username)

#отклик на вакансию
@app.route('/otklik/<status>/<username>/<itemid>', methods=['GET', 'POST'])
def otkliki(status, username, itemid):
    conn = cn.get_connection()
    curs = conn.cursor()
    userID = cn.getUserID(username)
    data = date.today()
    
    curs.execute("INSERT INTO otkliki (date_otklik, userid, number_v) VALUES (%s, %s, %s)", (data, userID, itemid))
    conn.commit()
    conn.close() 
    return redirect(url_for('profile', status=status, username=username))

# вакансия полностью
@app.route('/vacancy_cat_item/<status>/<username>/<industryURL>/<professionURL>/<itemid>', methods=['GET', 'POST'])
def vacCatItem(itemid, industryURL, professionURL, status, username):
    userID = cn.getUserID(username)
    conn = get_connection2()
    cur = conn.cursor() 

    data = date.today()
    """ cur.execute("insert into view_vacancies (date_view, userid, number_v) values (%s, %s, %s)", (data, userID, itemid))
    conn.commit() """

    cur.execute('SELECT number_v, industry_name, post, about, salary_from, salary_to, exp_from, conditions, requirements, duties, schedule, date_vac FROM vacancy WHERE number_v = %s', (itemid,))
    result = cur.fetchall()
    vacancyInfo = list(sum(result , ()))
    conn.commit()

    cur.execute('SELECT name_firm FROM company WHERE userid = (select userid from vacancy where number_v = %s)', (itemid,))
    result = cur.fetchone()
    companyName = result[0]
    conn.commit()

    cur.execute('SELECT email, phone FROM person WHERE userid = (select userid from vacancy where number_v = %s)', (itemid,))
    result = cur.fetchall()
    contacts = list(sum(result , ()))
    conn.commit()
    return render_template("vacancy_cat_item.html", itemid=itemid, vacancyInfo=vacancyInfo, companyName=companyName, contacts=contacts, status=status, username=username, industryURL=industryURL, professionURL=professionURL)

# КАТАЛОГ ЗАДАНИЙ
# сферы деятельности
@app.route('/task_cat_areas/<status>/<username>')
def taskCatAreas(status, username):
    conn = get_connection2()
    cur = conn.cursor()
    counts = []
    areasURL = []

    cur.execute('SELECT area_name FROM area WHERE area_name in (select area_name from task) group by area_name')
    areas = cur.fetchall()
    conn.commit()

    areas = list(sum(areas, ()))

    for item in areas:
        cur.execute('SELECT count(*) FROM task WHERE area_name = %s', (item,))
        count = cur.fetchone()
        counts.append(count)
        conn.commit()

    counts = list(sum(counts, ()))

    for item in areas:
        itemUni = translitToURL(item)
        areasURL.append(itemUni)

    data = list(zip(areas, counts, areasURL))
    return render_template("task_cat_areas.html", data=data, status=status, username=username)

# список заданий
@app.route('/task_cat_list/<status>/<username>/<areaURL>')
def taskCatList(status, username, areaURL):
    area = areaURL
    conn = get_connection()
    cur = conn.cursor() 

    cur.execute('SELECT task_id, area_name, about_task, date_task, cost FROM task WHERE area_name = %s', (area,))
    taskInfo = cur.fetchall()
    conn.commit()
    return render_template("task_cat_list.html", taskInfo=taskInfo, areaURL=areaURL, status=status, username=username)

# задание полностью
@app.route('/task_cat_item/<status>/<username>/<areaURL>/<itemid>', methods=['GET', 'POST'])
def taskCatItem(status, username, areaURL, itemid):
    userID = cn.getUserID(username)
    conn = get_connection2()
    cur = conn.cursor() 
    
    cur.execute('SELECT task_id, area_name, about_task, date_task, cost FROM task WHERE task_id = %s', (itemid,))
    result = cur.fetchall()
    taskInfo = list(sum(result , ()))
    conn.commit()

    cur.execute('SELECT customer_name FROM customer WHERE userid = (select userid from task where task_id = %s)', (itemid,))
    result = cur.fetchone()
    customerName = result[0]
    conn.commit()

    cur.execute('SELECT email, phone FROM person WHERE userid = (select userid from task where task_id = %s)', (itemid,))
    result = cur.fetchall()
    contacts = list(sum(result , ()))
    conn.commit()
    return render_template("task_cat_item.html", taskInfo=taskInfo, customerName=customerName, contacts=contacts, status=status, username=username, areaURL=areaURL)

# заяка на задание
@app.route('/request/<status>/<username>/<itemid>', methods=['GET', 'POST'])
def request(status, username, itemid):
    conn = cn.get_connection()
    curs = conn.cursor()
    userID = cn.getUserID(username)
    data = date.today()
    
    curs.execute("INSERT INTO request (date_req, userid, task_id) VALUES (%s, %s, %s)", (data, userID, itemid))
    conn.commit()
    conn.close() 
    return redirect(url_for('profile', status=status, username=username))

# КАТАЛОГ ИСПОЛНИТЕЛЕЙ
# сферы деятельности
@app.route('/perf_cat_areas/<status>/<username>')
def perfCatAreas(status, username):
    conn = get_connection2()
    cur = conn.cursor()
    counts = []
    areasURL = []

    cur.execute('SELECT area_name FROM area WHERE area_name in (select area_name from performer)')
    areas = cur.fetchall()
    conn.commit()

    areas = list(sum(areas, ()))

    for item in areas:
        cur.execute('SELECT count(*) FROM performer WHERE area_name = %s', (item,))
        count = cur.fetchone()
        counts.append(count)
        conn.commit()

    counts = list(sum(counts, ()))

    for item in areas:
        itemUni = translitToURL(item)
        areasURL.append(itemUni)

    data = list(zip(areas, counts, areasURL))
    return render_template("perf_cat_areas.html", username=username, data=data, status=status)

# список исполнителей
@app.route('/perf_cat_list/<status>/<username>/<areaURL>')
def perfCatList(username, areaURL, status):
    conn = get_connection()
    cur = conn.cursor() 
    area = areaURL

    cur.execute('SELECT * FROM performer WHERE area_name = %s', (area,))
    perfInfo = cur.fetchall()
    conn.commit()
    return render_template("perf_cat_list.html", username=username, perfInfo=perfInfo, areaURL=areaURL, status=status)

# исполнитель полностью
@app.route('/perf_cat_item/<status>/<username>/<areaURL>/<itemid>', methods=['GET', 'POST'])
def perfCatItem(username, itemid, status, areaURL):    
    userID = cn.getUserID(username)
    conn = get_connection2()
    cur = conn.cursor() 

    cur.execute('SELECT * FROM performer WHERE userid = %s', (itemid,))
    result = cur.fetchall()
    perfInfo = list(sum(result , ()))
    conn.commit()

    cur.execute('SELECT email, phone FROM person WHERE userid = (select userid from performer where userid = %s)', (itemid,))
    result = cur.fetchall()
    contacts = list(sum(result , ()))
    conn.commit()
    return render_template("perf_cat_item.html", username=username, perfInfo=perfInfo, contacts=contacts, status=status, areaURL=areaURL)


# панель администратора
@app.route('/admin')
def admin():
    if g.user:
        return render_template("admin.html")

# АДМИНКА, ОТРАСЛИ И ДОЛЖНОСТИ
# добавление
@app.route('/admin_data_ip_add', methods=['GET', 'POST'])
def adminDataIPAdd():
    conn = cn.get_connection2()
    cur = conn.cursor()
    if g.user:
        #industries = selectColumn('industry_name', 'post_industry')
        #professions = selectColumn('post_name', 'post_industry')
        industries = Ind()
        professions = Prof()

        form = IpAddForm()

        if form.validate_on_submit():
            industry = form.industry.data
            profession = form.profession.data

            try:
                if industry not in industries:
                    cur.execute("insert into industry (name_industry) values (%s)", (industry, ))
                    conn.commit()
                if profession not in professions:
                    cur.execute("insert into post (name_post) values (%s)", (profession, ))
                    conn.commit()
                cur.execute("insert into post_industry (industry_name, post_name) values (%s, %s)", (industry, profession, ))
                conn.commit()
                cur.close()
                return redirect(url_for('adminDataIPAdd'))
            except psycopg2.Error:
                conn.rollback()
                return render_template("admin_data_ip_add.html", message='Данная отрасль или должность уже существует!', industries=industry, professions=profession, form=form)
    industries = selectColumn('name_industry', 'industry')
    professions = selectColumn('name_post', 'post')
    cur.execute('SELECT * FROM post_industry')
    result = cur.fetchall()
    conn.commit()
    return render_template("admin_data_ip_add.html", industries=industries, professions=professions, form=form, result = result)

# изменение отраслей
@app.route('/admin_data_ind_edit', methods=['GET', 'POST'])
def adminDataIndEdit():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = IndEditForm()

    if g.user:
        industries = selectColumn('name_industry', 'industry')

        if form.validate_on_submit():
            industryOld = form.industryOld.data
            industryNew = form.industryNew.data
            try:
                cur.execute("update industry set name_industry = %s WHERE name_industry = %s",
                            (industryNew, industryOld))
                conn.commit()            
                return redirect(url_for('adminDataIndEdit'))
            except psycopg2.Error:
                conn.rollback()
                return render_template("admin_data_ind_edit.html", message='Данная отрасль уже существует!', form=form)
    return render_template("admin_data_ind_edit.html", industries=industries, form=form)

# изменение должностей
@app.route('/admin_data_prof_edit', methods=['GET', 'POST'])
def adminDataProfEdit():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = ProfEditForm()

    if g.user:
        professions = selectColumn('name_post', 'post')

        if form.validate_on_submit():
            professionOld = form.professionOld.data
            professionNew = form.professionNew.data
            try:
                cur.execute("update post set name_post = %s WHERE name_post = %s",
                            (professionNew, professionOld))
                conn.commit()            
                return redirect(url_for('adminDataProfEdit'))
            except psycopg2.Error:
                conn.rollback()
                return render_template("admin_data_prof_edit.html", message='Данная должность уже существует!', form=form)
    return render_template("admin_data_prof_edit.html", professions=professions, form=form)    

# АДМИНКА, СФЕРЫ ДЕЯТЕЛЬНОСТИ
# добавление
@app.route('/admin_data_areas_add', methods=['GET', 'POST'])
def adminDataAreasAdd():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = AreasAddForm()

    if g.user:
        areas = selectColumn('area_name', 'area')

        if form.validate_on_submit():
            area = form.area.data

            try:
                cur.execute("insert into area (area_name) values (%s)", (area, ))
                conn.commit()
                return redirect(url_for('adminDataAreasAdd'))
            except psycopg2.Error:
                conn.rollback()
                return render_template("admin_data_areas_add.html", message='Данная сфера деятельности уже существует!', form=form)
    cur.execute('SELECT * FROM area')
    result = cur.fetchall()
    result = [i[0] for i in result]
    conn.commit()
    return render_template("admin_data_areas_add.html", areas=areas, form=form, result=result)

# изменение
@app.route('/admin_data_areas_edit', methods=['GET', 'POST'])
def adminDataAreasEdit():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = AreasEditForm()

    if g.user:
        areas = selectColumn('area_name', 'area')

        if form.validate_on_submit():
            areaOld = form.areaOld.data
            areaNew = form.areaNew.data

            try:
                cur.execute("update area set area_name = %s WHERE area_name = %s", (areaNew, areaOld))
                conn.commit()
                return redirect(url_for('adminDataAreasEdit'))
            except psycopg2.Error:
                conn.rollback()
                return render_template("admin_data_areas_edit.html", message='Данная сфера деятельности уже существует!', form=form)
    return render_template("admin_data_areas_edit.html", areas=areas, form=form)


# #АДМИНКА, ОЦЕНКА РЕЗЮМЕ
@app.route('/rating/<status>/<username>/<industryURL>/<professionURL>/<userid>/<itemid>', methods=['GET', 'POST'])
def adminRatingResume(userid, itemid, industryURL, professionURL, status, username):
    conn = get_connection2()
    cur = conn.cursor()
    formRating = RatingResume()

    if formRating.validate_on_submit():
        rat = formRating.data
        try:
            cur.execute('UPDATE summary set rating = %s WHERE number_s = %s', (rat, itemid,))
            conn.commit()
            conn.close()
        except psycopg2.Error:
            conn.rollback()
    return render_template("summ_cat_item.html", itemid=itemid, userid=userid, cvInfo=cvInfo, fullName=fullName, contacts=contacts, status=status, username=username, industryURL=industryURL, professionURL=professionURL)
    

# АДМИНКА, УДАЛЕНИЕ
# удаление резюме
@app.route('/admin_delete_summ', methods=['GET', 'POST'])
def adminDeleteSumm():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = DateForm()

    if g.user and form.validate_on_submit():
        date = form.date.data
        cur.execute('SELECT number_s FROM summary WHERE date_summ::date < %s::date', (date,))
        result = cur.fetchone()
        cur.execute('delete from view_summary where number_s = %s', (result))
        cur.execute('delete from summary where date_summ::date < %s::date', (date,))
        conn.commit()
        return render_template("admin_delete_summ.html", form=form, message="Данные успешно удалены!")
    return render_template("admin_delete_summ.html", form=form)

# удаление вакансий
@app.route('/admin_delete_vacancy', methods=['GET', 'POST'])
def adminDeleteVacancy():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = DateForm()

    if g.user and form.validate_on_submit():
        date = form.date.data
        cur.execute('SELECT number_v FROM vacancy WHERE date_vac::date < %s::date', (date,))
        result = cur.fetchone()
        cur.execute('delete from view_vacancies where number_v = %s', (result))
        cur.execute('delete from vacancy where date_vac::date < %s::date', (date,))
        conn.commit()
        return render_template("admin_delete_vacancy.html", form=form, message="Данные успешно удалены!")
    return render_template("admin_delete_vacancy.html", form=form)

# удаление заданий
@app.route('/admin_delete_task', methods=['GET', 'POST'])
def adminDeleteTask():
    conn = cn.get_connection2()
    cur = conn.cursor()
    form = DateForm()

    if g.user and form.validate_on_submit():
        date = form.date.data

        cur.execute('delete from task where date_task::date < %s::date', (date,))
        conn.commit()
        return render_template("admin_delete_task.html", form=form, message="Данные успешно удалены!")
    return render_template("admin_delete_task.html", form=form)


# удаление сессии
@app.route('/dropsession')
def dropsession():
    session.pop('user', None)
    return redirect(url_for('index'))

