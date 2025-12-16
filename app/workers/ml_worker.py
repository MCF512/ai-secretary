import json
import pika
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.base import SessionLocal
from app.models.prediction import PredictionDB
from app.models.calendar_event import CalendarEventDB
from classes import TextToCommandModel


class MLWorker:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.model = None
        self._initialize_model()

    def _initialize_model(self):
        self.model = TextToCommandModel(model_path="dummy_path")
        self.model.load_model()

    def _connect(self):
        credentials = pika.PlainCredentials(
            settings.RABBITMQ_USER,
            settings.RABBITMQ_PASSWORD
        )
        parameters = pika.ConnectionParameters(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            credentials=credentials,
            heartbeat=600,
            blocked_connection_timeout=300
        )
        self.connection = pika.BlockingConnection(parameters)
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=settings.RABBITMQ_QUEUE, durable=True)
        self.channel.basic_qos(prefetch_count=1)

    def _validate_task(self, task_data: Dict[str, Any]) -> bool:
        required_fields = ['task_id', 'user_id', 'task_type', 'input_data', 'prediction_id']
        if not all(field in task_data for field in required_fields):
            return False
        
        if task_data.get('task_type') not in ['text_to_command']:
            return False
        
        if not task_data.get('input_data') or len(task_data.get('input_data', '')) == 0:
            return False
        
        return True

    def _process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            if not self._validate_task(task_data):
                return {
                    'task_id': task_data.get('task_id'),
                    'prediction_id': task_data.get('prediction_id'),
                    'status': 'failed',
                    'error': 'Invalid task data'
                }

            input_text = task_data['input_data']
            result = self.model.predict(input_text)
            
            output_data = json.dumps(result)
            confidence = result.get('confidence', 0.0)

            return {
                'task_id': task_data['task_id'],
                'prediction_id': task_data['prediction_id'],
                'output_data': output_data,
                'confidence': confidence,
                'status': 'completed'
            }
        except Exception as e:
            return {
                'task_id': task_data.get('task_id'),
                'prediction_id': task_data.get('prediction_id'),
                'status': 'failed',
                'error': str(e)
            }

    def _save_result(self, result: Dict[str, Any]):
        db: Session = SessionLocal()
        try:
            prediction = db.query(PredictionDB).filter(
                PredictionDB.id == result['prediction_id']
            ).first()
            
            if prediction:
                prediction.output_data = result.get('output_data')
                prediction.confidence = result.get('confidence')

                try:
                    payload = json.loads(result.get('output_data') or "{}")
                except json.JSONDecodeError:
                    payload = {}

                if payload.get("command_type") == "create_event":
                    params = payload.get("parameters") or {}
                    title = params.get("title") or prediction.input_data
                    start_time_str = params.get("start_time")
                    end_time_str = params.get("end_time")

                    from datetime import datetime

                    if start_time_str:
                        try:
                            start_time = datetime.fromisoformat(start_time_str)
                        except ValueError:
                            start_time = prediction.created_at
                    else:
                        start_time = prediction.created_at

                    end_time = None
                    if end_time_str:
                        try:
                            end_time = datetime.fromisoformat(end_time_str)
                        except ValueError:
                            end_time = None

                    event = CalendarEventDB(
                        user_id=prediction.user_id,
                        title=title,
                        description=None,
                        start_time=start_time,
                        end_time=end_time,
                        location=None,
                    )
                    db.add(event)

                db.commit()
        except Exception as e:
            print(f"Error saving result: {e}")
            db.rollback()
        finally:
            db.close()

    def _callback(self, ch, method, properties, body):
        try:
            task_data = json.loads(body)
            print(f"Received task: {task_data.get('task_id')}")
            
            result = self._process_task(task_data)
            self._save_result(result)
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
            print(f"Task {result['task_id']} processed with status: {result['status']}")
        except Exception as e:
            print(f"Error processing task: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def start(self):
        print("Starting ML Worker...")
        try:
            self._connect()
            print(f"Waiting for messages in queue: {settings.RABBITMQ_QUEUE}")
            
            self.channel.basic_consume(
                queue=settings.RABBITMQ_QUEUE,
                on_message_callback=self._callback
            )
            
            try:
                self.channel.start_consuming()
            except KeyboardInterrupt:
                print("Stopping worker...")
                self.channel.stop_consuming()
                if self.connection and not self.connection.is_closed:
                    self.connection.close()
        except Exception as e:
            print(f"Error starting worker: {e}")
            if self.connection and not self.connection.is_closed:
                self.connection.close()
            raise

