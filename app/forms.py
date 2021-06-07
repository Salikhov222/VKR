from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, RadioField, DateField, SelectField, IntegerField, BooleanField, SubmitField
from wtforms.validators import InputRequired, Length, DataRequired, Optional, Email, Regexp, EqualTo, ValidationError
from initdb import *
import initdb as cn
import phonenumbers
from app.models import User


def Ind():
    industriesSelect = []
    industries = selectColumn('name_industry', 'industry')
    for i in industries:
        industriesSelect.append((i, i))
    return industriesSelect

def Prof():
    professionsSelect = []
    professions = selectColumn('name_post', 'post')
    for i in professions:
        professionsSelect.append((i, i))
    return professionsSelect    

def Area():
    areasSelect  = []
    areas = selectColumn('area_name', 'area')
    for i in areas:
        areasSelect.append((i, i))
    return areasSelect   

class LoginForm(FlaskForm):
    login = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Sign In')

class SignUpForm(FlaskForm):
    login = StringField('Логин', validators=[InputRequired('Не введен логин'), Length(max=15, message='Логин не должен превышать 15 символов'), Regexp('^[A-Za-z0-9_]+$', message="Логин должен содержать только латинские буквы, цифры и _")])
    password = PasswordField('Пароль', validators=[InputRequired('Не введен пароль'), Regexp('^[a-zA-Z0-9_]+$', message="Пароль должен содержать только латинские буквы, цифры и _")])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    email = StringField('Email', validators=[InputRequired("Не введен email"), Email("Не похоже на email")])
    phone = StringField('Телефон', validators=[InputRequired('Не введен телефон'), Regexp('^[-+()0-9\s]+$', message="Не похоже на телефон")])
    status = RadioField('Выберите статус: ', choices=[('company', 'Работодатель'), ('employee', 'Соискатель'), ('customer', 'Заказчик'), ('performer', 'Исполнитель')])

    def validate_login(self, login):
        """проверка login на повтор"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM person WHERE login = %s;"
        curs.execute(sql, (login.data,))
        result = curs.fetchone()
        conn.close()
        if result is not None:
            raise ValidationError('Логин занят!')

    def validate_email(self, email):
        """проверка login на повтор"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM person WHERE email = %s;"
        curs.execute(sql, (email.data,))
        result = curs.fetchone()
        conn.close()
        if result is not None:
            raise ValidationError('Email занят!')        

    def validate_phone(self, phone):
        """проверка login на повтор"""
        conn = cn.get_connection()
        curs = conn.cursor()
        sql = "SELECT * FROM person WHERE phone = %s;"
        curs.execute(sql, (phone.data,))
        result = curs.fetchone()
        conn.close()
        if result is not None:
            raise ValidationError('Телефон занят!')

class PwRecForm(FlaskForm):
    login = StringField('Введите логин: ', validators=[InputRequired('Не введен логин')])
    passwordOld = PasswordField('Введите новый пароль: ', validators=[InputRequired('Не введен пароль')])
    passwordNew = PasswordField('Введите новый пароль еще раз: ', validators=[InputRequired('Не введен пароль')])

class IpAddForm(FlaskForm):
    industry = StringField('Введите отрасль: ', validators=[InputRequired('Не введена отрасль'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])
    profession = StringField('Введите соответствующую ей должность: ', validators=[InputRequired('Не введена должность'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])

class IndEditForm(FlaskForm):
    industryOld = StringField('Введите старое название отрасли: ', validators=[InputRequired('Не введена отрасль'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])
    industryNew = StringField('Введите новое название отрасли: ', validators=[InputRequired('Не введена отрасль'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])

class ProfEditForm(FlaskForm):
    professionOld = StringField('Введите старое название должности: ', validators=[InputRequired('Не введена должность'), Regexp('^[А-яёа-яёa-zA-Z0-9,\-\s]+$', message="Вводите русскими буквами")])
    professionNew = StringField('Введите новое название должности: ', validators=[InputRequired('Не введена должность'), Regexp('^[А-яёа-яёa-zA-Z0-9,\-\s]+$', message="Вводите русскими буквами")])

class AreasAddForm(FlaskForm):
    area = StringField('Введите сферу деятельности: ', validators=[InputRequired('Не введена сфера деятельности'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])

class AreasEditForm(FlaskForm):
    areaOld = StringField('Введите сферу деятельности: ', validators=[InputRequired('Не введена сфера деятельности'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])
    areaNew = StringField('Введите новое название: ', validators=[InputRequired('Не введена сфера деятельности'), Regexp('^[А-яёа-яё,\-\s]+$', message="Вводите русскими буквами")])


class DateForm(FlaskForm):
    date = DateField('', format='%Y-%m-%d', validators=[DataRequired('Дата введена в неправильном формате!')])

class ProfEdCompanyForm(FlaskForm):
    inn = StringField('ИНН: ')
    companyName = StringField('Название фирмы: ')
    companyBalance = StringField('Баланс фирмы: ', default='0')
    companyEmployer_name = StringField('Имя работодателя: ')
    companyEmployer_surname = StringField('Фамилия работодателя: ')
    companyPhone = StringField('Телефон фирмы: ')
    companyEmail = StringField('E-mail фирмы: ')

class ProfEdEmployeeForm(FlaskForm):
    fullName = StringField('ФИО: ')
    sex = SelectField('Ваш пол: ', choices=[('Мужской', 'Мужской'), ('Женский', 'Женский')])
    age = StringField('Ваш возраст: ')
    employeePhone = StringField('Телефон: ')
    employeeEmail = StringField('E-mail: ')
    
class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[DataRequired(message="Это обязательное поле")])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(message="Это обязательное поле")])
    new_password2 = PasswordField('Повторите новый пароль', validators=[DataRequired(message="Это обязательное поле"), EqualTo('new_password', message='Пароли должны совпадать')])
    submit = SubmitField('Изменить пароль')

class ProfEdCustomerForm(FlaskForm):
    customerName = StringField('Имя: ')
    customerPhone = StringField('Телефон: ')
    customerEmail = StringField('E-mail: ')
    customerBalance = StringField('Баланс: ', default='0')
    customerAbout = StringField('О себе: ')

class ProfEdPerformerForm(FlaskForm):
    performerName = StringField('Имя: ')
    performerArea = SelectField('Выберите сферу деятельности: ', choices = Area())
    performerAbout = StringField('О своей деятельности:  ')
    performerPhone = StringField('Телефон: ')
    performerEmail = StringField('e-mail: ')
    def UpArea(self):
        self.performerArea.choices = Area()

class BalanceForm(FlaskForm):
    balance = StringField('', validators=[InputRequired('Не введена сумма!'), Regexp('^[0-9\s]+$', message="Не похоже на сумму")])

class CreateItemCompanyForm(FlaskForm):
    industryName = SelectField('Выберите отрасль*: ', choices=Ind())
    professionName = SelectField('Выберите должность*: ', choices=Prof())
    about = StringField('Описание: ')
    minSalary = StringField('Минимальная заработная плата, руб (числом): ')
    maxSalary = StringField('Максимальная заработная плата, руб (числом): ')
    minExp = IntegerField('Минимальный опыт работы, лет (числом, если без опыта, то 0)*: ', validators=[Optional(strip_whitespace=False), InputRequired()])
    conditions = StringField('Условия: ')
    requirements = StringField('Требования: ')
    duties = StringField('Обязанности: ')
    empType = SelectField('Выберите тип занятости: ', choices=[('полная', 'полная'), ('частичная', 'частичная'), ('вахта', 'вахта'), ('удаленная работа', 'удаленная работа'), ('стажировка', 'стажировка')])
    def UpInd(self):
        self.industryName.choices = Ind()
    def UpProf(self):
        self.professionName.choices = Prof()    

class CreateItemEmployeeForm(FlaskForm):
    industryName = SelectField('Выберите отрасль*: ', choices = Ind() )
    professionName = SelectField('Выберите должность*: ', choices = Prof() )
    minSalary = StringField('Минимальная заработная плата, руб (числом): ')
    maxSalary = StringField('Максимальная заработная плата, руб (числом): ')
    exp = IntegerField('Опыт работы, лет (числом, если без опыта, то 0)*: ', validators=[Optional(strip_whitespace=False), InputRequired('Не введен опыт работы')])
    edType = SelectField('Уровень образования: ', 
                         choices=[('', ''), ('Среднее', 'Cреднее'), ('Среднее специальное', 'Среднее специальное'), ('Неоконченное высшее', 'Неоконченное высшее'),
                                   ('Высшее', 'Высшее')])
    edInst = StringField('Учебное заведение: ')
    skills = StringField('Навыки: ')
    empType = SelectField('Выберите тип занятости: ',
                          choices=[('полная', 'полная'), ('частичная', 'частичная'), ('вахта', 'вахта'),
                                   ('удаленная работа', 'удаленная работа'), ('стажировка', 'стажировка')])
    def UpInd(self):
        self.industryName.choices = Ind()
    def UpProf(self):
        self.professionName.choices = Prof()                                  

class CreateItemCustomerForm(FlaskForm):
    areaName = SelectField('Выберите сферу деятельности*: ', choices=Area())
    taskAbout = StringField('Опишите задание*: ', validators=[InputRequired('Не введено описание задания')])
    dateInput = DateField('Введите дату выполнения в формате ГГГГ-ММ-ДД*: ', format='%Y-%m-%d', validators=[DataRequired('Дата введена в неправильном формате!')])
    price = IntegerField('Стоимость выполнения (числом, в рублях)*: ', validators=[Optional(strip_whitespace=False), InputRequired('Не введена стоимость выполнения')])
    def UpArea(self):
        self.areaName.choices = Area()

class RatingResume(FlaskForm):
    rating = SelectField('Оцените резюме от 1 до 5: ',  choices=[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)], coerce=int,  validate_choice=True)

     