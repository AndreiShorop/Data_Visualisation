# 📚 API_REFERENCE.md

## 🧱 Основные зависимости
- `pandas>=2.0.0`
- `streamlit>=1.58.0`
- `plotly>=5.0.0`
- `bcrypt>=4.0.0`

---

## 🛠️ Классы и функциональность

### `AuthService` — [app/services/auth_service.py](app/services/auth_service.py)
*Управление сессиями и доступом.*

| Метод | Аргументы | Описание |
| :--- | :--- | :--- |
| `register_user` | `username, password` | Хеширует пароль и сохраняет в `users.db`. |
| `verify_user` | `username, password` | Проверяет соответствие пароля. |
| `add_user_widget` | `username, widget_config` | Сохраняет JSON-конфигурацию виджета для пользователя. |
| `get_user_widgets` | `username` | Возвращает список всех сохраненных виджетов. |

### `ExportService` — [app/services/export_service.py](app/services/export_service.py)
*Безопасная выгрузка данных.*

| Метод | Аргументы | Описание |
| :--- | :--- | :--- |
| `to_excel` | `df, filename` | Сохраняет DataFrame в Excel с очисткой от Formula Injection. |
| `quality_report_to_pdf` | `results, output_path` | Генерация PDF-отчета о качестве данных. |

### `QualityService` — [app/services/quality_service.py](app/services/quality_service.py)
*Модуль аналитики качества.*

| Метод | Аргументы | Описание |
| :--- | :--- | :--- |
| `audit_dataset` | `df` | Запускает полный аудит (Missing, Dups, Outliers). |
| `calculate_quality_score` | `results` | Рассчитывает итоговый % качества данных. |

### `DatasetRegistryService` — [app/services/dataset_registry_service.py](app/services/dataset_registry_service.py)
*Реестр данных.*

| Метод | Аргументы | Описание |
| :--- | :--- | :--- |
| `register_new_dataset` | `key, name, path` | Добавляет новую запись в `datasets_config.json`. |
| `get_all_datasets` | - | Возвращает словарь всех доступных датасетов. |

---

## 🏗️ Модели данных (`app/models/state.py`)
Проект использует типизированные состояния (Session State) для отслеживания выбранных фильтров, текущего пользователя и активного набора данных. 
*Примечание: Состояние автоматически сбрасывается при закрытии вкладки браузера.*
