# ЛР4 — Базовый системный дизайн (склад)

Монолитное приложение `warehouse/` декомпозировано на два независимых микросервиса, взаимодействующих по gRPC.

## Структура проекта

```
LR1-empty/
├── pom.xml                    # родительский Maven-проект
├── grpc-contract/             # IDL: proto-контракты gRPC
├── warehouse-reference/       # Reference Service — справочники и валидация
├── warehouse-core/              # Core Service — бизнес-логика и UI
└── warehouse/                 # исходный монолит (не изменялся)
```

## Модули

| Модуль | Назначение |
|--------|------------|
| **grpc-contract** | Файл `reference.proto`, генерация Java-stub'ов |
| **warehouse-reference** | gRPC-сервер: каталог категорий, валидация товаров, правила соседства |
| **warehouse-core** | gRPC-клиент + склад: транзакции, состояние, консольный интерфейс |

## Запуск

### IntelliJ IDEA

1. Откройте корневой `pom.xml` → правый клик → **Add as Maven Project** (или иконка Maven → Reload).
2. Дождитесь индексации. В Project появятся модули `grpc-contract`, `warehouse-reference`, `warehouse-core`.
3. Запустите конфигурации из выпадающего списка Run (созданы в `.idea/runConfigurations/`):
   - **warehouse-reference** — сначала (порт 50051)
   - **warehouse-core** — затем
4. Либо: правый клик на `ReferenceServiceMain.java` → Run, затем на `warehouse-core/.../Main.java` → Run.

Старый `warehouse/src/Main.java` — монолит, для ЛР4 не используется.

### Терминал

```bash
mvn install -DskipTests

# Терминал 1 — справочный сервис (порт 50051)
mvn -pl warehouse-reference exec:java

# Терминал 2 — основной сервис
mvn -pl warehouse-core exec:java
```

Переменные окружения для Core Service: `REFERENCE_HOST` (по умолчанию `127.0.0.1`), `REFERENCE_PORT` (по умолчанию `50051`).

## gRPC API

Сервис `ReferenceService` (`grpc-contract/src/main/proto/reference.proto`):

- `ListCategories` — каталог категорий товаров
- `ValidateProduct` — проверка корректности товара
- `CanStoreTogether` — проверка совместимости категорий при хранении
- `GetNeighborhoodRadius` — радиус проверки соседства ячеек

Trace ID передаётся в metadata `trace-id` и логируется в обоих сервисах.

Подробное описание работы — в файле [ОТЧЕТ_ЛР4.md](ОТЧЕТ_ЛР4.md).
