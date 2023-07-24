# stock_alert
Create a stock alert website using frontend and backend systems

pip install -r requirements.txt

Inspiration: https://medium.com/illumination/how-to-build-a-stock-price-alert-using-python-d7d61ec12f2

### Install Flask:

https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3#step-4-setting-up-the-database

pip install flask

python -c "import flask; print(flask.__version__)"

### Install Pandas

https://pandas.pydata.org/docs/getting_started/install.html

pip install pandas

### Install Werzug

https://pypi.org/project/Werkzeug/

pip install -U Werkzeug

### Utilize Alpha Vantage API

https://www.alphavantage.co/#about

pip install alpha_vantage

"For individual usage, a unique API key is required to access financial data

### Run Website:

export FLASK_APP=app

flask run

### Initialize database:

python3 init_db.py

### Install Flask-Login:

https://pypi.org/project/Flask-Login/

pip install flask-login

### Install SQLAlchemy

pip install SQLAlchemy

### Search Tab

Insert as many or as little ticket symbols which you have filed alerts for e.g. NDAQ, MSFT, AAPL, NOC...
Clicking submit will check whether alerts need to be filed for your stock posts. If alerts have been filed, 
the stock symbol will be present along with various other details from your post and from stock data.

### New Post Tab

Insert one valid stock symbol, a ceiling, and a floor to create a post.

### Install MySQL

Install MySQL depending on OS: https://dev.mysql.com/doc/mysql-installation-excerpt/8.0/en/

pip install cryptography

Update line 19 in app.py to tailor to your password and user: mysql_manager = MySqlDb(host = 'localhost', user = 'root', password = ?, db = ?)