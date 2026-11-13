import json

from kafka import KafkaConsumer, KafkaProducer
from trace_utils import trace_span

BOOTSTRAP_SERVER = "localhost:9092"
INPUT_TOPIC = "s2604_inbox"
OUTPUT_TOPIC = "s2604_tasks"


consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    group_id="s2604-planner",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    ),
)

producer = KafkaProducer(
    bootstrap_servers=BOOTSTRAP_SERVER,
    value_serializer=lambda value: json.dumps(value).encode(
        "utf-8"
    ),
)


print("Planner is ready and listening...")


for record in consumer:
    message = record.value
    trace_id = message["correlation_id"]

    with trace_span(trace_id, "planner"):
        print("Planner received:", json.dumps(message))

        task = {
            "correlation_id": trace_id,
            "role": "planner",
            "question": message["question"],
            "plan": [
                "Identify the main topic",
                "Prepare a concise answer",
                "Send the plan to the writer",
            ],
        }

        producer.send(OUTPUT_TOPIC, value=task)
        producer.flush()

        print("Planner sent:", json.dumps(task))