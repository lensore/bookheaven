from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, EqualTo, Length, Email, Optional


class LoginForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    email = EmailField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Текущий пароль', validators=[DataRequired(), Length(min=6, max=128)])
    new_password = PasswordField('Новый пароль', validators=[DataRequired(), Length(min=6, max=128)])
    confirm_new_password = PasswordField(
        'Повторите новый пароль',
        validators=[DataRequired(), EqualTo('new_password')],
    )
    submit = SubmitField('Сменить пароль')


class ProfileForm(FlaskForm):
    name = StringField('Name', validators=[Length(max=128)])
    email = EmailField('Email', validators=[DataRequired(), Email(), Length(max=256)], render_kw={'readonly': True})
    address = StringField('Address', validators=[Length(max=256)])
    payment_method = StringField('Payment method', validators=[Length(max=128)])
    submit = SubmitField('Save changes')


class CatalogForm(FlaskForm):
    query = StringField(
        'Search',
        validators=[Optional(), Length(max=255)],
        render_kw={"placeholder": "Search for books, authors, ISBN..."},
    )
    category = SelectField(
        'Category',
        validators=[Optional()],
        choices=[('', 'Все категории')],
    )
    sort = SelectField(
        'Sort',
        validators=[Optional()],
        choices=[
            ('', 'Без сортировки'),
            ('price_asc', 'Цена: низкая → высокая'),
            ('price_desc', 'Цена: высокая → низкая'),
        ],
    )

    def __init__(self, *args, categories=None, **kwargs):
        super().__init__(*args, **kwargs)
        category_choices = [('', 'Все категории')]
        if categories:
            category_choices.extend((category, category) for category in categories)
        self.category.choices = category_choices
