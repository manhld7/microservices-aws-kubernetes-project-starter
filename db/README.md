```bash
docker build --build-arg DB_PASSWORD=postgres --build-arg DB_USERNAME=123456 . -t analytics-db:1
```

```bash
docker run -p 5433:5432 analytics-db:1
```
