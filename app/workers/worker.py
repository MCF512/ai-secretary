from app.workers.ml_worker import MLWorker


if __name__ == "__main__":
    worker = MLWorker()
    worker.start()

