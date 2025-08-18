# Wagtail Admin Login URL

A **Wagtail** package to enhance the security of the Wagtail admin login page by allowing administrators to configure a **custom login URL**, apply **IP whitelisting/blacklisting**, enable **optional throttling**, and view **detailed login logs** directly from the admin dashboard.

## ✨ Features

- 🔒 **Custom Admin Login URL**
  Hide the default `/admin/login/` endpoint by specifying your own secure path.
  Example: `/secret-portal/`

- ⚙️ **Enable/Disable from Dashboard**
  Easily toggle the custom login URL setting without touching code.

- 🛡️ **IP Whitelisting & Blacklisting**
  Restrict access to the admin login page by allowing or blocking specific IP ranges.

- ⏳ **Optional Login Throttling**
  Protect against brute force attacks by limiting repeated login attempts.

- 📑 **Login Logs**
  Track login activity, including failed attempts, directly from Wagtail’s **Reports** menu.

## 📦 Installation

```bash
pip install wagtail-admin-login-url
```

Add to your `INSTALLED_APPS` in **settings.py**:

```python
INSTALLED_APPS = [
    ...
    'wagtail_admin_login_url',
    ...
]
```

## ⚙️ Configuration

### Middleware

Add the middleware to your **MIDDLEWARE** list:

```python
MIDDLEWARE = [
    ...
    "wagtail_admin_login_url.middleware.AdminLoginURLMiddleware",
]
```

### Migrate Wagtail Admin URL

```bash
python manage.py migrate wagtail_admin_login_url
```

## ⚙️ Usage

### Settings

In **Wagtail Admin > Settings > Admin Login URL**, you can configure:

- **Enable Custom URL**: Toggle to enable or disable custom login URL.
- **Custom Admin Path**: Set your custom path (e.g. `/my-secret-admin/`).
- **IP Whitelist**: Allow access only from specified IPs (optional).
- **IP Blacklist**: Block access from specified IPs (optional).
- **Throttling**: Limit login attempts per IP (optional).
- **Logging**: Enable or disable login attempt logging.

![Wagtail Admin URL Settings Screenshot](https://raw.githubusercontent.com/dazzymlv/wagtail-admin-login-url/main/docs/static/screenshot-settings-0.1.0-dev.1.png)

### Reports

- Login activity is available under **Reports > Admin Login Logs**.
- Includes details such as:

  - IP Address
  - Timestamp
  - Username (if provided)
  - Success/Failure status
  - Reason (blocked, throttled, etc.)

![Wagtail Admin Screenshot](https://raw.githubusercontent.com/dazzymlv/wagtail-admin-login-url/main/docs/static/screenshot-reports-0.1.0-dev.1.png)

## 🔒 Security Notes

- Use this package as an additional **security-through-obscurity** layer.
- Always combine with:

  - Strong passwords
  - Multi-Factor Authentication (MFA)
  - Proper server-level hardening

## ⚙️ Testing

```bash
python -m unittest discover tests
```

## 📜 License

This project is licensed under the **MIT License**.

## 🙌 Contributing

Contributions are welcome!
Please open issues and pull requests on the [GitHub repository](https://github.com/dazzymlv/wagtail-admin-login-url).
