import json

from kafka import KafkaConsumer, KafkaProducer
from trace_utils import trace_span

BOOTSTRAP_SERVER = "localhost:9092"
INPUT_TOPIC = "s2604_drafts"
OUTPUT_TOPIC = "s2604_final"


consumer = KafkaConsumer(
    INPUT_TOPIC,
    bootstrap_servers=BOOTSTRAP_SERVER,
    group_id="s2604-reviewer",
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


print("Reviewer is ready and listening...")


for record in consumer:
    draft = record.value
    trace_id = draft["correlation_id"]

    with trace_span(trace_id, "reviewer"):
        print("Reviewer received:", json.dumps(draft))

        answer = draft.get("draft", "").strip()

        if answer:
            final_message = {
                "correlation_id": trace_id,
                "status": "approved",
                "answer": answer,
                "review": "Draft contains a non-empty answer.",
            }
        else:
            final_message = {
                "correlation_id": trace_id,
                "status": "rejected",
                "answer": "",
                "review": "Draft was empty.",
            }

        producer.send(OUTPUT_TOPIC, value=final_message)
        producer.flush()

        print("Reviewer sent:", json.dumps(final_message))