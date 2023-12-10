import re
import jwt
import yaml
from yaml import SafeLoader
from pathlib import Path
import streamlit as st
from datetime import datetime, timedelta
import extra_streamlit_components as stx

ROOT_PATH = str(Path(__file__).parent)


class Validator:
    """
    This class will check the validity of the entered username, password, and email for a
    newly registered user.
    """

    @staticmethod
    def validate_name(name: str) -> bool:
        return 1 < len(name) < 100

    @staticmethod
    def validate_username(username: str) -> bool:
        pattern = r"^[a-zA-Z0-9_-]{1,20}$"
        return bool(re.match(pattern, username))

    @staticmethod
    def validate_email(email: str) -> bool:
        return "@" in email and 2 < len(email) < 320


class Authenticator:
    """
    This class will create login, register user
    """

    def __init__(self):
        """
        Create a new instance of "Authenticate"
        """
        with open(ROOT_PATH + '/config.yaml') as file:
            self.config = yaml.load(file, Loader=SafeLoader)
        self.usernames = [v['username'] for v in self.config['credentials']['names'].values()]
        self.passwords = [v['password'] for v in self.config['credentials']['names'].values()]
        self.authentication = dict(zip(self.usernames, self.passwords))
        self.emails = [v['email'] for v in self.config['credentials']['names'].values()]
        self.cookie_name = self.config['cookie']['name']
        self.cookie_signature_key = self.config['cookie']['key']
        self.cookie_expiry_second = self.config['cookie']['expiry_seconds']
        self.cookie_manager = stx.CookieManager()

    def _set_exp_date(self) -> int:
        """
        Creates the re-authentication cookie's expiry date.
        """
        expire = int((datetime.now() + timedelta(
            seconds=self.cookie_expiry_second
        )).strftime("%Y%m%d%H%M%S"))

        return expire

    def _jwt_encode(self) -> str:
        """
        Encodes the contents of the re-authentication cookie.
        """
        expire = self._set_exp_date()
        encoded_jwt = jwt.encode({
            'username': st.session_state['username'],
            'password': st.session_state['password'],
            'expire': expire},
            self.cookie_signature_key, algorithm='HS256'
        )

        return encoded_jwt

    def _jwt_decode(self) -> str:
        """
        Decodes the contents of the re-authentication cookie.
        """
        try:
            return jwt.decode(self.encoded_jwt, self.cookie_signature_key, algorithms=['HS256'])
        except:
            return False

    def _set_cookie(self):
        """
        Set cookie for re-authentication.
        """
        self.cookie_manager.set(self.cookie_name, self.encoded_jwt,
                                expires_at=datetime.now() + timedelta(seconds=self.cookie_expiry_second))

    def _check_cookie(self):
        """
        Checks the existence of the re-authentication cookie and get information if exists.
        """
        self.encoded_jwt = self.cookie_manager.get(self.cookie_name)
        if self.encoded_jwt is not None:
            information = self._jwt_decode()
            st.session_state['username'] = information['username']
            st.session_state['password'] = information['password']
            st.session_state['authentication_status'] = True

    def _check_credentials(self, inplace: bool = True) -> bool:
        """
        Checks the validity of the entered credentials.
        """
        if st.session_state['username'] in self.usernames:
            try:
                if st.session_state['password'] == self.authentication[st.session_state['username']]:
                    if inplace:
                        self.encoded_jwt = self._jwt_encode()
                        self._set_cookie()
                        st.session_state['authentication_status'] = True
                    else:
                        return True
                else:
                    if inplace:
                        st.session_state['authentication_status'] = False
                    else:
                        return False
            except Exception as e:
                print(e)
        else:
            if inplace:
                st.session_state['authentication_status'] = False
            else:
                return False

    def login(self, location: str = 'main') -> tuple:
        """
        Creates a login widget.

        Parameters
        ----------
        location: str
            The location of the login form i.e. main or sidebar.
        Returns
        -------
        str
            Name of the authenticated username.
        str
            Authenticated password.
        bool
            The status of authentication, None: no credentials entered,
            False: incorrect credentials, True: correct credentials.
        """

        if 'username' not in st.session_state:
            st.session_state['username'] = None
        if 'password' not in st.session_state:
            st.session_state['password'] = None
        if 'authentication_status' not in st.session_state:
            st.session_state['authentication_status'] = None
        if 'logout' not in st.session_state:
            st.session_state['logout'] = None

        if not st.session_state['authentication_status']:
            self._check_cookie()
            if not st.session_state['authentication_status']:
                if location == 'main':
                    login_form = st.form('Login')
                elif location == 'sidebar':
                    login_form = st.sidebar.form('Login')

                username = login_form.text_input('Username').lower()
                st.session_state['username'] = username
                password = login_form.text_input('Password', type='password')
                st.session_state['password'] = password

                if login_form.form_submit_button('Login'):
                    self._check_credentials()
        # print(st.session_state['username'])
        # print(st.session_state['password'])
        # print(st.session_state['authentication_status'])

        # if st.session_state["authentication_status"]:
        #     st.write(f'Welcome *{st.session_state["username"]}*')
        #     st.title('Some content')
        # elif st.session_state["authentication_status"] is False:
        #     st.sidebar.error('Username/password is incorrect')
        # elif st.session_state["authentication_status"] is None:
        #     st.sidebar.warning('Please enter your username and password')

        return st.session_state['username'], st.session_state['password'], st.session_state['authentication_status']

    def _register_credentials(self, name: str, username: str, password: str, email: str, preauthorization: bool = True):
        """
        Adds to credentials dictionary the new user's information.

        Parameters
        ----------
        name: str
            The name of the new user.
        username: str
            The username of the new user.
        password: str
            The password of the new user.
        email: str
            The email of the new user.
        preauthorization: bool
            The pre-authorization requirement,
            True: user must be preauthorized to register,
            False: any user can register.
        """
        if not Validator.validate_username(name):
            st.sidebar.error('Name is not valid')
        if not Validator.validate_username(username):
            st.sidebar.error('Username is not valid')
        if not Validator.validate_email(email):
            st.sidebar.error('Email is not valid')
        self.config['credentials']['names'][username] = {
            'email': email,
            'username': username,
            'password': password,
        }
        if preauthorization:
            self.config['preauthorized']['emails'].remove(email)
        # print(self.config)
        with open(ROOT_PATH + '/config.yaml', 'w') as file:
            yaml.dump(self.config, file, default_flow_style=False)

    def register_user(self, location: str = 'main', preauthorization=True) -> bool:
        """
        Creates a register new user widget.
        Returns
        -------
        bool
            The status of registering the new user, True: user registered successfully.
        """
        if preauthorization:
            if not self.config['preauthorized']['emails']:
                st.sidebar.error("Pre-authorization argument must not be None")
        if location == 'main':
            register_user_form = st.form('Register user')
        elif location == 'sidebar':
            register_user_form = st.sidebar.form('Register user')

        new_email = register_user_form.text_input('Email')
        new_name = register_user_form.text_input('Name')
        new_username = register_user_form.text_input('Username').lower()
        new_password = register_user_form.text_input('Password', type='password')
        new_password_repeat = register_user_form.text_input('Repeat password', type='password')

        if register_user_form.form_submit_button('Register'):
            if len(new_email) and len(new_username) and len(new_name) and len(new_password) > 0:
                if new_username not in self.usernames:
                    if new_password == new_password_repeat:
                        if preauthorization:
                            if new_email in self.config['preauthorized']['emails']:
                                self._register_credentials(new_username, new_name, new_password, new_email,
                                                           preauthorization)
                                return True
                            else:
                                st.sidebar.error('User not preauthorized to register')
                        else:
                            self._register_credentials(new_username, new_name, new_password, new_email,
                                                       preauthorization)
                            return True
                    else:
                        st.sidebar.error('Passwords do not match')
                else:
                    st.sidebar.error('Username already taken')
            else:
                st.sidebar.error('Please enter an email, username, name, and password')


# if __name__ == '__main__':
#     authenticator = Authenticator()
#     authenticator.login('Login')
#     authenticator.register_user('Register', preauthorization=True)
