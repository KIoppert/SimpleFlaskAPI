from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


class UserCreateForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()])
    last_name = StringField('Фамилия', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Создать пользователя')

class PostCreateForm(FlaskForm):
    author_id = StringField('ID автора', validators=[DataRequired()])
    title = StringField('Заголовок', validators=[DataRequired()])
    text = StringField('Текст', validators=[DataRequired()])
    submit = SubmitField('Создать пост')