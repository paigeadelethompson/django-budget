# Django Budget

## Quickstart

### From source
- pip install poetry
- *Clone this repository*
- poetry build 
- pip install dist/*.whl

### Post Install 
- django_budget_admin makemigrations budget transaction category dashboard summary admin
- django_budget_admin migrate
- django_budget_admin collectstatic
- django_budget_admin createsuperuser
- django_budget_admin runserver
