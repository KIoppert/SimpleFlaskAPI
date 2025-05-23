
# 🧪 SimpleFlaskAPI

SimpleFlaskAPI — это простой, но функциональный RESTful API, построенный на Flask. Он реализует базовые социальные функции: регистрацию пользователей, создание постов и систему реакций.
Проект разработан в учебных целях и сопровождается модульными тестами.

## 🚀 Основные возможности

- Регистрация пользователей с валидацией email
- Публикация постов пользователями
- Добавление реакций к постам (❤️ 💥 👍 👎)
- Получение информации о пользователях и постах
- Сортировка постов и пользователей по активности
- Визуализация активности пользователей

## 📁 Структура проекта
```
SimpleFlaskAPI/
├── app/
│ ├── init.py # Инициализация приложения
│ ├── models.py # Определения моделей данных
│ ├── routes.py # Определения маршрутов API
│ └── utils.py # Вспомогательные функции
├── tests/ # Модульные тесты (pytest)
│ ├── test_users.py
│ ├── test_posts.py
│ └── test_reactions.py
├── main.py # Точка входа в приложение
└── README.md # Документация
```
## 🧑‍💻 Запуск
Клонирование репозитория:
```bash
git clone https://github.com/KIoppert/SimpleFlaskAPI.git
cd SimpleFlaskAPI
```
Создание виртуального окружения
```bash
python -m venv venv
source venv/bin/activate  # Для Windows: venv\Scripts\activate
```
Установка завиимостей
```bash
pip install -r requirements.txt
```
Запуск:
```bash
python main.py
```
## 🧪 Тестирование
```bash
pytest tests/
```
