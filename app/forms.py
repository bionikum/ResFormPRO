from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError
import re

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[
        DataRequired(),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    confirm_password = PasswordField('Подтвердите пароль', validators=[
        DataRequired(),
        EqualTo('password', message='Пароли должны совпадать')
    ])
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')
    
    def validate_password(self, field):
        password = field.data
        if len(password) < 6:
            raise ValidationError('Пароль должен быть не менее 6 символов')
        if not re.search(r'[A-Za-z]', password) or not re.search(r'\d', password):
            raise ValidationError('Пароль должен содержать буквы и цифры')

class PhotoUploadForm(FlaskForm):
    body_front = TextAreaField('Комментарий к фото тела спереди')
    body_side = TextAreaField('Комментарий к фото тела сбоку')
    body_back = TextAreaField('Комментарий к фото тела сзади')
    face_front = TextAreaField('Комментарий к фото лица спереди')
    face_side = TextAreaField('Комментарий к фото лица сбоку')
    submit = SubmitField('Загрузить фотографии')

class RecommendationForm(FlaskForm):
    title = StringField('Название рекомендации', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    category = SelectField('Категория', choices=[
        ('posture', 'Осанка'),
        ('symmetry', 'Симметрия'),
        ('exercises', 'Упражнения'),
        ('general', 'Общие рекомендации')
    ])
    difficulty = SelectField('Сложность', choices=[
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый')
    ])
    submit = SubmitField('Сохранить рекомендацию')
