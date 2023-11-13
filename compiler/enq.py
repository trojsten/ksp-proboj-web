from celery import Celery

app = Celery("enq", broker="redis://localhost")

app.send_task("compiler.compile_player", queue="compile", kwargs={"source_url": "http://localhost:8080/p.zip", "language": "cpp", "report_url": ""})

print("sent task")
