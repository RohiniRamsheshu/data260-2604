import json

from kafka import KafkaConsumer, KafkaProducer
from trace_utils import trace_span

BOOTSTRAP_SERVER = "localhost:9092"
INPUT_TOPIC = "s2604_tasks"
OUTPUT_TOPIC = "s2604_drafts"


consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    group_id="s2604-writer",
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


print("Writer is ready and listening...")


for record in consumer:
    task = record.value
    trace_id = task["correlation_id"]

    with trace_span(trace_id, "writer"):
        print("Writer received:", json.dumps(task))

        draft = {
            "correlation_id": trace_id,
            "role": "writer",
            "question": task["question"],
            "draft": (
                "This is a concise answer based on the planner's "
                "instructions: "
                + task["question"]
            ),
            "plan_used": task["plan"],
        }

        producer.send(OUTPUT_TOPIC, value=draft)
        producer.flush()

        print("Writer sent:", json.dumps(draft))