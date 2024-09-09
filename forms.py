from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, PasswordField, SubmitField, DateField, TextAreaField
from wtforms.validators import DataRequired, Length


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Registrar')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')


class TaskForm(FlaskForm):
    task_title = StringField('Titulo da Task', validators=[DataRequired()])
    task_assignee = SelectField('Responsavel', coerce=str, validators=[DataRequired()])
    task_status = SelectField('Status', coerce=str, validators=[DataRequired()])
    task_date = DateField('Data da Task', format='%Y-%m-%d', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    submit = SubmitField('Criar Task')
