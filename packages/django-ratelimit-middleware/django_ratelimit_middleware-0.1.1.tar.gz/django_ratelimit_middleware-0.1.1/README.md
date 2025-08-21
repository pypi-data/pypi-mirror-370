# django-ratelimit-middleware


[![codecov](https://codecov.io/gh/k3y5tr0k3/django-ratelimit-middleware/branch/master/graph/badge.svg?token=nkXbpqFJot)](https://codecov.io/gh/k3y5tr0k3/django-ratelimit-middleware)
[![Python - >=3.12](https://img.shields.io/badge/Python->=3.12-2ea44f?logo=python&logoColor=yellow)](https://www.python.org/)
[![Django - >=5.2](https://img.shields.io/badge/Django->=5.2-2ea44f?logo=django&logoColor=lime)](https://www.djangoproject.com/)
[![Style - Black](https://img.shields.io/badge/Style-Black-black?logo=stylelint&logoColor=white)](https://github.com/psf/black)


## 🌟 Overview

**Django Rate Limit Middleware** is a simple, lightweight Django middleware for rate limiting requests based on **user identity** or **IP address**.  
It helps prevent abuse, brute force attacks, and excessive traffic with **minimal configuration**.


## ✨ Features

- 🔑 Supports **anonymous and authenticated** users
- ⏱ Configurable **request count and time window**
- 🧠 Uses Django’s **cache framework**
- 🪶 Lightweight, dependency-free


## 📦 Installation

```bash
pip install django-ratelimit-middleware
```


## ⚙️ Configuration

Add to your `MIDDLEWARE`:

```python
MIDDLEWARE = [
    ...
    "django_ratelimit_middleware.middleware.RateLimitMiddleware",
]
```

Add settings:

```python
RATE_LIMIT_REQUESTS = 100       # Number of requests allowed
RATE_LIMIT_WINDOW = 60          # Window in seconds
```

## 🚀 Usage

After installation and config, all views are automatically rate-limited.  
Example response when exceeding the limit:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```

## 🧪 Running Tests

```bash
pytest
```

## 📊 Coverage

Coverage reports are uploaded to [**Codecov**](https://codecov.io)


## 🤝 Contributing

Contributions are welcome! 🎉

See [CONTRIBUTING.md](CONTRIBUTING.md) for details.


## 📌 Roadmap

- [ ] Custom rate limit strategies (e.g., per endpoint)
- [ ] Redis backend example
- [ ] Admin dashboard for monitoring blocked IPs
- [ ] Configurable responses (JSON, HTML)
- [ ] Turnstile feature


## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Disclaimer

This software is provided "as is", without warranty of any kind, express or implied, including but not limited to the warranties of merchantability, fitness for a particular purpose and noninfringement.  
In no event shall the authors or copyright holders be liable for any claim, damages, or other liability, whether in an action of contract, tort, or otherwise, arising from, out of, or in connection with the software or the use or other dealings in the software.  
Use at your own risk.


## 👨‍💻 Author

Maintained with ❤️ by [K3y5tr0k3](https://github.com/k3y5tr0k3).




