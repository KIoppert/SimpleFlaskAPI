from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email


class UserCreateForm(FlaskForm):
    first_name = StringField('Имя', validators=[DataRequired()],
                        render_kw={"placeholder": "Иван", "class": "form-control"})
    last_name = StringField('Фамилия', validators=[DataRequired()],
                        render_kw={"placeholder": "Иванов", "class": "form-control"})
    email = StringField('Email', validators=[DataRequired(), Email()],
                        render_kw={"placeholder": "Ivanov@examle.com", "class": "form-control"})
    submit = SubmitField('Создать пользователя')


class PostCreateForm(FlaskForm):
    author_id = StringField('ID автора', validators=[DataRequired()],
                        render_kw={"placeholder": "0", "class": "form-control"})
    title = StringField('Заголовок', validators=[DataRequired()],
                        render_kw={"placeholder": "Как правильно ...", "class": "form-control"})
    text = StringField('Текст', validators=[DataRequired()],
                        render_kw={"placeholder": "Необходимо позаботиться о ...", "class": "form-control"})
    submit = SubmitField('Создать пост')
