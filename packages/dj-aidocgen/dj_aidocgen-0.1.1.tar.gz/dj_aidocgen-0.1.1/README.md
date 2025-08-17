# dj-aidocgen

Генератор документации для Django endpoint'ов:
- подробное описание алгоритма
- последовательность действий (классы/методы)
- C4 (Container)
- диаграмма (Structurizr PNG или Mermaid)
- Structurizr DSL

## Установка (локально)
pip install -e .

## Использование
export DJANGO_SETTINGS_MODULE=myproj.settings
export OPENAI_API_KEY=sk-...  # опционально
dj-aidocgen --app users --handle user-detail --alg-name get_user_detail --diagram structurizr
