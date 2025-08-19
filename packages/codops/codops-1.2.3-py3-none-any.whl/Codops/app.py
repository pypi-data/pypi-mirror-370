# import os
# import secrets
# from urllib.parse import urlencode

# import requests
# from dotenv import load_dotenv
# from flask import Flask, redirect, request, session, url_for

# # Attempt to load environment variables from .env file
# try:
#     load_dotenv()
# except FileNotFoundError:
#     print(".env file not found, using default values.")

# app = Flask(__name__)
# # Generate a random 32-character hex key
# app.secret_key = secrets.token_hex(16)

# # GitHub OAuth Config
# CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
# CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
# REDIRECT_URI = "http://localhost:5000/login/oauth/callback"


# @app.route("/")
# def index():
#     if "github_token" in session:
#         return '<h1>Welcome!</h1><a href="/profile">View profile</a> | <a href="/logout">Logout</a>'
#     return '<h1>Home</h1><a href="/login">Login with GitHub</a>'


# @app.route("/login")
# def login():
#     params = {
#         "client_id": CLIENT_ID,
#         "redirect_uri": REDIRECT_URI,
#         "scope": "user:email",
#         "state": os.urandom(16).hex(),
#     }
#     # http://localhost:8080//login/oauth/callback
#     auth_url = f"https://github.com/login/oauth/authorize?{urlencode(params)}"
#     return redirect(auth_url)


# @app.route("/login/oauth/callback")
# def callback():
#     if "error" in request.args:
#         return f"Error: {request.args['error']}"

#     if "code" in request.args:
#         # Exchange code for token
#         response = requests.post(
#             "https://github.com/login/oauth/access_token",
#             data={
#                 "client_id": CLIENT_ID,
#                 "client_secret": CLIENT_SECRET,
#                 "code": request.args["code"],
#                 "redirect_uri": REDIRECT_URI,
#             },
#             headers={"Accept": "application/json"},
#         )

#         token_data = response.json()
#         if "access_token" in token_data:
#             session["github_token"] = token_data["access_token"]
#             return redirect(url_for("profile"))

#     return "Authentication failed", 401


# @app.route("/profile")
# def profile():
#     if "github_token" not in session:
#         return redirect(url_for("login"))

#     headers = {
#         "Authorization": f"Bearer {session['github_token']}",
#         "Accept": "application/vnd.github.v3+json",
#     }

#     user_data = requests.get(
#         "https://api.github.com/user", headers=headers
#     ).json()
#     emails = requests.get(
#         "https://api.github.com/user/emails", headers=headers
#     ).json()

#     return f"""
#         <h1>Profile</h1>
#         <img src="{user_data['avatar_url']}" width="100">
#         <p>Name: {user_data.get('name', 'N/A')}</p>
#         <p>Email: {next(e['email'] for e in emails if e['primary'])}</p>
#         <a href="/logout">Logout</a>
#     """


# @app.route("/logout")
# def logout():
#     session.pop("github_token", None)
#     return redirect(url_for("index"))


# if __name__ == "__main__":
#     app.run(debug=True)

from flask import Flask, redirect, url_for, session, request, render_template
import requests
import os
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# GitHub OAuth configuration
GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login')
def login():
    return redirect(f'https://github.com/login/oauth/authorize?client_id={GITHUB_CLIENT_ID}')


@app.route('/login/oauth/callback')
def callback():
    code = request.args.get('code')
    token_url = 'https://github.com/login/oauth/access_token'
    token_data = {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code
    }
    token_headers = {'Accept': 'application/json'}
    token_response = requests.post(token_url, data=token_data, headers=token_headers)
    token_json = token_response.json()
    session['access_token'] = token_json.get('access_token')
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'access_token' in session:
        return render_template('index.html', authenticated=True)
    return redirect(url_for('home'))


@app.route('/ask', methods=['POST'])
def ask():
   if openai.api_key is None:
    print("La clé API n'est pas définie. Vérifiez vos variables d'environnement.")
   else: 
    if 'access_token' not in session:
        return redirect(url_for('home'))

    command = request.form['command']
    response = openai.ChatCompletion.create(
        model="gpt-4.1",
        messages=[{"role": "user", "content": command}]
    )
    answer = response['choices'][0]['message']['content']
    return render_template('index.html', authenticated=True, answer=answer)

def launch_app():
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)