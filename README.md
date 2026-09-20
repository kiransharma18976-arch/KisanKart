# KisanKart

KisanKart is a B2B agricultural marketplace that directly connects farmers with bulk buyers without intermediaries, while enabling surplus food redistribution through NGOs.

## Core Workflow

**Farmer → Bulk Buyer → NGO**

- Farmers list agricultural products.
- Bulk buyers can purchase products directly from farmers.
- Bulk buyers can list surplus edible food.
- NGOs can receive notifications about available surplus food and coordinate collection/distribution.

## Technology

- Python / Flask
- MySQL
- HTML, CSS, JavaScript

## Local Setup

1. Install dependencies: `pip install -r requirements.txt`
2. Set database environment variables using `.env.example` as a guide.
3. Run: `python app.py`

## Deployment

For production, set `SECRET_KEY`, `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, and `DB_NAME` as environment variables and use `gunicorn app:app` as the start command.
