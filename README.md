# 📊 Analytical Platform Pro

![Platform Banner](https://via.placeholder.com/1200x400?text=Analytical+Platform+Pro+v2.0)

[![Python Version](https://img.shields.io/badge/python-3.13%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.58%2B-orange.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Security](https://img.shields.io/badge/security-audited-brightgreen.svg)](#security)

**Analytical Platform Pro** — это комплексное решение для профессионального анализа, визуализации и аудита качества данных. Построенное на базе Streamlit и современных инженерных паттернов, приложение предоставляет инструменты уровня SaaS для работы с табличными данными в реальном времени.

---

## 🎯 Ключевые возможности

| Модуль | Описание |
| :--- | :--- |
| **📁 Interactive Table** | Исследование данных с мощной фильтрацией, глобальным поиском и динамическим отображением. |
| **🎯 Data Quality** | Глубокий аудит датасетов: поиск пропусков, дубликатов, выбросов и структурных ошибок с расчетом Quality Score. |
| **🛠️ Dashboard Builder** | Визуальный конструктор графиков (Bar, Line, Scatter, Pie и др.) с сохранением состояния в БД. |
| **🔄 Dataset Comparison** | Статистическое сравнение двух версий данных, выявление изменений в структуре и значениях. |
| **📤 Upload Data** | Динамическая загрузка и регистрация новых CSV-файлов без перезагрузки кода. |
| **🔐 Secure Export** | Экспорт защищенных Excel (Formula Injection Protection) и PDF отчетов. |

---

## 🏗️ Архитектура проекта

Приложение следует принципам **Clean Architecture** и **Service-Oriented Design**, что обеспечивает масштабируемость и легкость тестирования.

```mermaid
graph TD
    A[Streamlit UI Layer] --> B[Controller Layer]
    B --> C[Service Layer]
    C --> D[Data Access / DB Layer]
    C --> E[Third-party Services]
    
    subgraph Services
        C1[AuthService]
        C2[QualityService]
        C3[ExportService]
        C4[DatasetRegistry]
    end
```

---

## 🛠️ Технологический стек

- **Core:** Python 3.13+, Pandas, NumPy, SciPy
- **UI:** Streamlit, Plotly, Matplotlib
- **Security:** Bcrypt, SQL Injection Protection, Formula Injection Sanitization
- **Reports:** Sweetviz, FPDF2, Openpyxl
- **Database:** SQLite3

---

## 🚀 Быстрый старт

### 1. Установка окружения
```bash
# Клонирование репозитория
git clone https://github.com/your-repo/analytical-platform-pro.git
cd analytical-platform-pro

# Создание виртуального окружения
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Установка зависимостей
pip install -r requirements.txt
```

### 2. Инициализация базы данных
Перед первым запуском необходимо создать базу данных и пользователя:
```bash
python init_database.py
```
> **Default Access:** `admin` | `admin123`

### 3. Запуск приложения
```bash
streamlit run streamlit_app.py
```

---

## 📂 Структура проекта

```text
├── app/
│   ├── services/     # Бизнес-логика (Auth, Export, Quality, etc.)
│   ├── reports/      # Генерация HTML и PDF отчетов
│   ├── models/       # Типизированные структуры данных
│   ├── ui/           # Компоненты интерфейса
│   └── config.py     # Глобальные настройки путей
├── data/             # Наборы данных (FIFA, Movies, Powerlifting)
├── docs/             # Техническая документация
├── html_reports/     # Сгенерированные аналитические отчеты
├── streamlit_app.py  # Точка входа веб-приложения
└── users.db          # База данных пользователей и виджетов
```

---

## 🛡️ Безопасность

- **Аутентификация:** Хеширование паролей с использованием `bcrypt`.
- **Excel Protection:** Автоматическая защита от Formula Injection (префиксация спецсимволов `'`).
- **Data Isolation:** Виджеты дашбордов привязаны к конкретному пользователю в БД.
- **Path Sanitization:** Валидация путей при загрузке новых датасетов.

Для подробностей см. [SECURITY.md](docs/SECURITY.md).

---

## 🗺️ Roadmap

- [ ] Интеграция с SQL базами данных (PostgreSQL/MySQL).
- [ ] Расширенный модуль ML-прогнозирования.
- [ ] Экспорт дашбордов в интерактивный HTML-формат.
- [ ] Поддержка многопользовательского редактирования одного дашборда.

---

© 2026 Analytical Platform Pro. Разработано профессионалами для профессионалов.
