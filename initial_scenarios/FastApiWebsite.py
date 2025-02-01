from .BaseScenario import BaseScenario
from message import Message


class FastApiWebsite(BaseScenario):
    name = "FastAPI website scenario"
    
    def run(self):
        yield Message(role="user", content="Инициализируй проект", hide=True)
        yield Message(role="assistant", content="""Хорошо, давайте инициализируем базовый проект на FastAPI
<workspace>
    <shell id="main">git init</shell>
    <shell id="main">git branch -m main</shell>
    <shell id="main">pip install --upgrade pip</shell>
    <shell id="runtime">pip install fastapi fastapi[all]</shell>
</workspace>
<workspace>
    <code filename="templates/base/header.html">
<header>
    <h5>{{ title }}</h5>
</header></code>
</workspace>
<workspace>
    <code filename="templates/base/footer.html">
<footer>
    <p>&copy; 2025 {{ WebSiteName }}. All rights reserved.</p>
</footer></code>
</workspace>
<workspace>
    <code filename="templates/base/base.html">
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %} - {{ WebSiteName }}{% endblock %}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
</head>
<body>
    {% include 'base/header.html' %}
    
    <div class="content">
        {% block content %}
        <!-- Основное содержимое страницы -->
        {% endblock %}
    </div>
    
    {% include 'base/footer.html' %}
</body>
</html></code>
</workspace>
<workspace>
    <code filename="templates/index.html">
{% extends 'base/base.html' %}

{% block title %}Главная{% endblock %}

{% block content %}
<h1>Welcome to the Home Page</h1>
<p>This is the main page of our website.</p>
{% endblock %}</code>
</workspace>
<workspace>
    <code filename="routes/index.py">
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html", context={"WebSiteName": "BaseProject"}
    )</code>
</workspace>
<workspace>
    <code filename="main.py">
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes.index import router as index_router

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(index_router)</code>
</workspace>
<workspace>
    <code filename="README.md">
# BaseProject

Этот проект представляет собой базовую структуру веб-приложения на основе FastAPI с использованием шаблонизатора Jinja2 и CSS-фреймворка TailwindCSS.

## Структура проекта

```
.
├── app/
│   ├── routes/
│   │   └── index.py
│   └── main.py
├── static/
│   └── styles.css
├── templates/
│   ├── base/
│   │   ├── base.html
│   │   ├── header.html
│   │   └── footer.html
│   └── index.html
├── requirements.txt
└── README.md
```

## Установка зависимостей

Для установки необходимых зависимостей выполните следующую команду:

```bash
pip install -r requirements.txt
```

## Запуск приложения

Для запуска приложения выполните следующую команду:

```bash
uvicorn app.main:app --reload
```

После этого приложение будет доступно по адресу [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

## Описание файлов

- **app/routes/index.py**: Определяет маршруты для приложения. В данном случае маршрут для главной страницы.
- **app/main.py**: Основной файл приложения, где происходит монтирование статических файлов и подключение маршрутов.
- **static/styles.css**: Файл для пользовательских стилей.
- **templates/base/base.html**: Базовый шаблон, который включает в себя шапку, основное содержимое и подвал.
- **templates/base/header.html**: Шаблон для шапки сайта.
- **templates/base/footer.html**: Шаблон для подвала сайта.
- **templates/index.html**: Главная страница сайта, которая расширяет базовый шаблон.
- **requirements.txt**: Список необходимых Python-пакетов для работы приложения.

## Лицензия

Этот проект распространяется под лицензией MIT. Подробности см. в файле [LICENSE](LICENSE).</code>
</workspace>
<workspace>
    <code filename=".gitignore">
__pycache__/
*.py[cod]
*$py.class</code>
</workspace>
<workspace>
    <shell id="main">mkdir static</shell>
    <shell id="main">pip freeze > requirements.txt</shell>
    <shell id="main">git add .</shell>
    <shell id="main">git commit -m "initial commit"</shell>
    <shell id="runtime">uvicorn main:app --reload</shell>
</workspace>

Я создал и запустил базовый проект. Вы можете проверить его по адресу http://127.0.0.1:8000""", hide=True)
        yield Message(role="user", content="Подключи tailwind через cdn", hide=True)
        yield Message(role="assistant", content="""Давайте подключим TailwindCSS через cdn в файл base.html
<workspace>
    <code filename="templates/base/base.html">
        <code-replace>
            <original>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            </original>
            <new>
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css">
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css">
            </new>
        </code-replace>
    </code>
</workspace>
Сделаем коммит и перезапустим проект для приминения изменений
<workspace>
    <shell id="main">git add .</shell>
    <shell id="main">git commit -m "add tailwindcss cdn"</shell>
    <shell id="runtime">uvicorn main:app --reload</shell>
</workspace>""", hide=True)
        
