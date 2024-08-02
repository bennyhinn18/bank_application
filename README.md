### Title
**Bank App Using Django**

### Aim
To develop a web-based bank application using Django framework that allows users to register, log in, manage their accounts, perform transactions (deposit and withdraw), and view transaction history.

### Procedure

#### 1. **Project Setup**

1. **Install Django:**
   ```bash
   pip install django
   ```
2. **Create a New Django Project:**
   ```bash
   django-admin startproject bank_app
   cd bank_app
   ```
3. **Create a New App:**
   ```bash
   python manage.py startapp accounts
   ```

#### 2. **Define Models**

In `accounts/models.py`:

```python
from django.db import models
from django.contrib.auth.models import User

class Account(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
```

#### 3. **Create Forms**

In `accounts/forms.py`:

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class TransactionForm(forms.Form):
    TRANSACTION_TYPES = (
        ('deposit', 'Deposit'),
        ('withdraw', 'Withdraw'),
    )
    transaction_type = forms.ChoiceField(choices=TRANSACTION_TYPES)
    amount = forms.DecimalField(max_digits=10, decimal_places=2)
```

#### 4. **Create Views**

In `accounts/views.py`:

```python
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, TransactionForm
from .models import Account, Transaction

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Account.objects.create(user=user)
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    account = Account.objects.get(user=request.user)
    transactions = Transaction.objects.filter(account=account).order_by('-created_at')
    return render(request, 'accounts/home.html', {'account': account, 'transactions': transactions})

@login_required
def transaction(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            account = Account.objects.get(user=request.user)
            transaction_type = form.cleaned_data['transaction_type']
            amount = form.cleaned_data['amount']
            if transaction_type == 'deposit':
                account.balance += amount
            elif transaction_type == 'withdraw' and account.balance >= amount:
                account.balance -= amount
            account.save()
            Transaction.objects.create(account=account, amount=amount, transaction_type=transaction_type)
            return redirect('home')
    else:
        form = TransactionForm()
    return render(request, 'accounts/transaction.html', {'form': form})
```

#### 5. **Define URLs**

In `accounts/urls.py`:

```python
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('home/', views.home, name='home'),
    path('transaction/', views.transaction, name='transaction'),
]
```

In `bank_app/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('', include('django.contrib.auth.urls')),  # For login/logout functionality
]
```

#### 6. **Create Templates**

Create templates in `accounts/templates/accounts/`.

**base.html**:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    <link rel="stylesheet" type="text/css" href="{% static 'accounts/styles.css' %}">
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>
```

**register.html**:

```html
{% extends 'base.html' %}

{% block title %}Register{% endblock %}

{% block content %}
<h2>Register</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Register</button>
</form>
<a href="{% url 'login' %}">Login</a>
{% endblock %}
```

**login.html**:

```html
{% extends 'base.html' %}

{% block title %}Login{% endblock %}

{% block content %}
<h2>Login</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Login</button>
</form>
<a href="{% url 'register' %}">Register</a>
{% endblock %}
```

**home.html**:

```html
{% extends 'base.html' %}

{% block title %}Home{% endblock %}

{% block content %}
<h2>Welcome, {{ request.user.username }}</h2>
<p>Account Balance: {{ account.balance }}</p>
<a href="{% url 'transaction' %}">Make a Transaction</a>
<a href="{% url 'logout' %}">Logout</a>

<h3>Transaction History</h3>
<table>
    <thead>
        <tr>
            <th>Type</th>
            <th>Amount</th>
            <th>Date</th>
        </tr>
    </thead>
    <tbody>
        {% for transaction in transactions %}
        <tr>
            <td>{{ transaction.transaction_type }}</td>
            <td>{{ transaction.amount }}</td>
            <td>{{ transaction.created_at }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

**transaction.html**:

```html
{% extends 'base.html' %}

{% block title %}Transaction{% endblock %}

{% block content %}
<h2>Transaction</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Submit</button>
</form>
<a href="{% url 'home' %}">Back to Home</a>
{% endblock %}
```

#### 7. **Add Static Files and Basic Styling**

Create a directory for static files and add a CSS file.

**accounts/static/accounts/styles.css**:

```css
body {
    font-family: Arial, sans-serif;
    background-color: #f2f2f2;
    margin: 0;
    padding: 0;
}

h2, h3 {
    color: #333;
}

form {
    margin: 20px;
    padding: 20px;
    background: #fff;
    border: 1px solid #ddd;
}

table {
    width: 100%;
    border-collapse: collapse;
}

table, th, td {
    border: 1px solid #ddd;
}

th, td {
    padding: 8px;
    text-align: left;
}

a {
    display: block;
    margin: 20px 0;
}
```

#### 8. **Run the Application**

Apply the migrations and run the server:

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

Visit `http://127.0.0.1:8000/accounts/register/` to register a new user, then log in at `http://127.0.0.1:8000/accounts/login/` and start using your bank app.

### SQL for Tables

Here's the SQL code equivalent to the Django models for creating the database tables.

```sql
CREATE TABLE auth_user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(150) NOT NULL UNIQUE,
    password VARCHAR(128) NOT NULL,
    email VARCHAR(254) NULL,
    is_staff BOOLEAN NOT NULL,
    is_active BOOLEAN NOT NULL,
    is_superuser BOOLEAN NOT NULL,
    last_login DATETIME NULL,
    date_joined DATETIME NOT NULL
);

CREATE TABLE accounts_account (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE REFERENCES auth_user(id),
    balance DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE accounts_transaction (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER NOT NULL REFERENCES accounts_account(id),
    amount DECIMAL(10, 2) NOT NULL,
    transaction_type VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

### Overview of the Project

#### Project Description
This project is a simple bank application developed using the Django framework. The application allows users to:

- Register and log in.
- View their account balance.
- Perform deposit and withdrawal transactions.
- View their transaction history.

#### Features
1. **User Registration**: New users can register by providing a username and password.
2. **User Authentication**: Registered users can log in and log out.
3. **Account Management**: Each user has an associated account with a balance.
4. **Transactions**: Users can deposit or withdraw money from their account.
5. **Transaction History**: Users can view a history of all their transactions.

### How to Set Up and Connect Database

#### Prerequisites
- Python and pip installed.
- Django installed (`pip install django`).

#### Steps

1. **Create a Django Project**:
   ```bash
   django-admin startproject bank_app
   cd bank_app
   ```

2. **Create a Django App**:
   ```bash
   python manage.py startapp accounts
   ```

3. **Define Models**: Add the `Account` and `Transaction` models in `accounts/models.py`.

4. **Create Forms**: Add the user registration and transaction forms in `accounts/forms.py`.

5. **Create Views**: Implement the views for registration, login, logout, home, and transactions in `accounts/views.py`.

6. **Define URLs**: Set up the URL routing in `accounts/urls.py` and include it in `bank_app/urls.py`.

7. **Create Templates**: Develop the HTML templates for registration, login, home, and transaction pages.

8. **Static Files and Styling**: Add a CSS file for basic styling.

9. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

10. **Run the Server**:
    ```bash
    python manage.py runserver
    ```

11. **Access the Application**: Open a web browser and go to `http://127.0.0.1:8000/accounts/register/` to register a new user.

### Result

The bank application should now be up and running. Users can register, log in, view their account balance, perform transactions, and see their transaction history. Here are some sample results:

1. **Registration**: A new user can successfully register.
2. **Login**: A registered user can log in.
3. **Home Page**: The user sees their account balance and transaction history.
4. **Transaction**: The user can deposit or withdraw money.
5. **Transaction History**: The user sees a list of all their transactions.

### Sample Output

1. **Home Page**:
   ```
   Welcome, username
   Account Balance: 100.00
   Transaction History:
   | Type    | Amount | Date                |
   |---------|--------|---------------------|
   | Deposit | 50.00  | 2024-07-07 12:34:56 |
   | Withdraw| 20.00  | 2024-07-07 13:22:10 |
   ```

2. **Transaction Form**:
   ```
   Transaction
   [Transaction Type] [Deposit/Withdraw]
   [Amount] [_________]
   [Submit Button]
   ```

### Result

By following the outlined procedure, you have developed a fully functional web-based bank application using Django. The app includes user registration, authentication, account management, transactions, and a transaction history feature. This project provides a solid foundation for further enhancements and additional banking functionalities.
