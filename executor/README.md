# Proboj Executor

Proboj Executor sa stará o spúšťanie hier na serveri.
Cez Celery dostane údaje o hre, posťahuje si potrebné súbory z Proboj Webu
a po skončení hry nahrá výsledky.

## Konfigurácia

Viď [config.example.yml](config.example.yml).

## Spustenie

```shell
celery -A executor worker -Q execute
```

Ďalšie užitočné prepínače:
- `-c 2` zmena počtu workerov (predvolene počet CPU)
- `-l INFO` zobrazovanie INFO log správ

## Spustenie hry

```python  
app.send_task(
    "executor.run_match",
    queue="execute",
    kwargs={
        "game_id": 1,
        "server_url": "http://0.0.0.0:8080/srv",
        "server_version": "v1",
        "bundle_url": "http://0.0.0.0:8080/bundle.zip",
        "bundle_version": "v3",
        "players": [
            {
                "name": "masivak",
                "url": "http://0.0.0.0:8080/maverick.zip",
                "version": 2,
                "language": "py"
            },
            {
                "name": "maverick",
                "url": "http://0.0.0.0:8080/maverick.zip",
                "version": 1,
                "language": "py"
            }
        ],
        "args": "/bundle/maps/1.png",
        "report_url": "",
        "timeout": 1
    },
)
```
