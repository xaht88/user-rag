# Frontend Specification (Next.js + Tailwind)

## 1. Scope

Документ фиксирует целевую реализацию frontend-части ДЗ в связке с backend (`FastAPI`).

## 2. Stack

- Next.js (App Router), TypeScript
- Tailwind CSS
- Vitest + Testing Library

## 3. Feature Scope

1. Upload документов с состояниями `loading/error/success`
2. Chat по документам с источниками и ошибками запроса
3. Выбор LLM-провайдера и модели на уровне сессии

## 4. Architecture

```
rag_app/frontend_next/
  app/
  components/
  features/
  shared/
```

- `app/` — layout и маршруты
- `components/` — переиспользуемые UI-блоки
- `features/` — доменная логика по модулям
- `shared/` — API-клиент, типы и утилиты

## 5. Integration with FastAPI

- Dev:
  - frontend: `npm run dev` (порт `3000`)
  - backend: `uvicorn main:app --reload --port 8000`
- Build:
  - `npm run export:backend`
  - экспорт в `rag_app/backend/static/next`
  - template entry в `rag_app/backend/templates/next_index.html`

## 6. Responsive

- Desktop (`>= 1024px`): split-panel
- Tablet (`768px-1023px`): compact split-panel
- Mobile (`< 768px`): tab/drawer fallback

## 7. Acceptance Criteria

- Минимум 3 функции реализованы и проверены тестами
- Минимум 3 автотеста проходят
- UI корректно работает на desktop и mobile
