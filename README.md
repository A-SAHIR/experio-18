# EXPERIO

## 1. Installation

There are multiple ways to install experio depending on your OS:

### 1.1. docker-compose
Docker is available for all operating systems. We highly recommend going with this option.

Copy the config files:
- `experio.env -> .env`: Environment variables such as ports to use and default usernames, passwords, etc...
- `bluejay/sample.env -> bluejay/.env`: Environment variables for the bluejay container, generally API links to use.
- `experio.conf -> odoo.conf`: Odoo config's file
- `docker-compose.dev.yml -> docker-compose.yml`: The yaml file to start the dev server(change **dev** with **prod**) in the ports provided inside `.env`

Then run the following command:
```shell
make up
```

## Nginx
Change nginx conf to handle large and long requests by adding:
```conf
http {
        ####
        # Server Enhancements
        ####
        client_max_body_size 100M;
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
}
```

## 2. Setup
We're assuming that **experio** is installed. When creating databases, make sure you set the same username
and password for the administrator account.

We need two databases to get started:

### 2.1. base_global
This database is the main database we use to manage our entire server.

#### 2.1.1. Modules
We need to install:
- **exp_cognitive_bluejay**: This module will be used to send and receive request to the [Bluejay](https://bluejay.morosoft.ma) server, and it will install:
- **exp_multi_client**: This module will allow us to assign databases (i.e. portal access) to the clients.
- **exp_hr_employee**: This module install the HR features to create and invite new collaborators to the server.
- **code_backend_theme**: This is the backend theme we modified to create our own template.

We need to uninstall:
- **auth_totp**: This module is used for two-factor authentication. It complicates the mobile auth method.
- **sms**: This module sends SMS messages to the provided phone numbers
- **partner_autocomplete**: This module fetches logo from the internet for the partners.

> **Info**
> sometimes uninstalling `auth_totp` might automatically uninstall `partner_autocomplete` and `sms`

#### 2.1.2. Settings

- Set up the number of folders inside the general settings
- Choose *EXPERIO* as default window title
- Set up the SMTP configuration
- Set up the website, logo, send_email, cc_email and country_id in the company page

### 2.2. base_client
This database is the client database we copy from and create databases for new clients.

#### 2.2.1. Modules
We need to install:
- **exp_cognitive_receipt**: manage receipts. This will install:
  - **exp_cognitive**: Manage invoices and general documents.
- **account_standard_report**: Integration with prod systems.
- **code_backend_theme**: This is the backend theme we modified to create our own template.

We need to uninstall:
- **auth_totp**: This module is used for two-factor authentication. It complicates the mobile auth method.
- **partner_autocomplete**: This module fetches logo from the internet for the partners.
- **sms**: This module sends SMS messages to the provided phone numbers

#### 2.2.2. Settings

- Choose *EXPERIO* as default window title
- Set up the website, logo and country_id in the company page

## 3. Errors Table

The following table will hold code errors, their sources and most importantly, the explanation

| Code      | Source                                                | Description                                                                                                                          |
|-----------|-------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------|

## Modules Cleansing
- delete `web_unsplash` from `res.config`
- uninstall `iap_mail`, `payment_wire_transfer`, `mail_bot`, `fetchmail`, `web_unsplash`

## Postgres Commands
```shell
psql -Uroot -dcabinet_global
```

```sql
select id, state, request_uri from cognitive_invoice_token where request_uri='https://bluejay.experioservices.com/multiprocess' and state='sent';
```

```sql
update cognitive_invoice_token set state='pending' where request_uri='https://bluejay.experioservices.com/multiprocess' and state='sent';
```

**migration**:
```sql
select id, state, name from experio_migration_line;
update experio_migration_line set state='draft_invoice';
```
