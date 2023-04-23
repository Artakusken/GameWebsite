from flask import Flask, url_for, request, render_template, redirect, json, jsonify, make_response
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, BooleanField, SubmitField, EmailField, IntegerField
from wtforms.validators import DataRequired
from flask_restful import reqparse, abort, Api, Resource


from game_resources import *

server = "192.168.0.195"
port = 8080

site = Flask(__name__)
api = Api(site)
site.config["SECRET_KEY"] = "Github"
log_mg = LoginManager()
log_mg.init_app(site)


class RegistrationForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    nickname = StringField('Никнейм', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Зарегистрироваться')


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@site.route("/")
def front_page():
    # global_init("users")
    # session = create_session()
    return render_template("front_page.html", title="Гвинтецкий")


@site.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegistrationForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        global_init("users")
        session = create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже зарегестрирован")
        if session.query(User).filter(User.nickname == form.nickname.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой никнейм уже занят")
        user = User(
            nickname=form.nickname.data,
            email=form.email.data,
            hashed_password=form.password_again.data
        )
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        login_user(user, remember=form.remember_me.data)
        return redirect('/')
    return render_template('register.html', title='Регистрация', form=form)


@log_mg.user_loader
def load_user(user_id):
    global_init("users")
    session = create_session()
    return session.query(User).get(user_id)


@site.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        global_init("users")
        session = create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', title='Авторизация', form=form)


@site.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@site.route('/player/<username>')
def statistic(username):
    global_init("users")
    session = create_session()
    if isinstance(current_user, User) and session.query(User).filter(username.lower() == current_user.nickname.lower()).first():
        return render_template('profile_page.html', title='Профиль', user=current_user)
    for user in session.query(User).all():
        if user.nickname.lower() == username.lower():
            return render_template('player_page.html', title='Профиль', user=user)
    return render_template('error_page.html', title='Профиль не найден')


if __name__ == '__main__':

    api.add_resource(DeckResource, '/api/v2/my_deck/<deck_cards>')
    api.add_resource(CardsResource, '/api/v2/my_deck/constructor')
    api.add_resource(PlayerResource, '/api/v2/player/<email>&<password>')

    site.run(port=port, host=server)
