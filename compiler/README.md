# Proboj Compiler

Proboj Compiler sa stará o kompiláciu hráčov.
Cez Celery dostane ZIP súbor zo zdrojákmi, skompiluje ich v Podman
kontajneri a výsledok pošle späť Proboj Webu.

## Konfigurácia

```yaml
# config.yml

# Podman configuration
podman:
  # Socket URL
  url: unix:///run/user/1000/podman/podman.sock

# Celery configuration
celery:
  # Broker URL
  broker: redis://localhost
  
  # Other Celery options can be set here.
  # https://docs.celeryq.dev/en/stable/userguide/configuration.html#configuration

# Compilation images (language -> image name)
images:
  # See compiler-cpp-image for example of such image.
  cpp: localhost/cmp:latest
```

## Spustenie

```shell
celery -A compiler worker -Q compile
```

Ďalšie užitočné prepínače:
- `-c 2` zmena počtu workerov (predvolene počet CPU)
- `-l INFO` zobrazovanie INFO log správ

## Volanie kompilácie

```python
app.send_task(
    "compiler.compile_player",
    queue="compile",
    kwargs={
        "source_url": "", 
        "language": "cpp", 
        "report_url": "",
    },
)
```

- `source_url` adresa, odkiaľ si Compiler stiahne ZIP so zdrojákmi
- `language` jazyk, ktorý bude použitý na kompiláciu
- `report_url` adresa, kam Compiler pošle výsledok kompilácie
