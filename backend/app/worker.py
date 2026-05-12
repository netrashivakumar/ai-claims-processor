import pika
import json
from sentence_transformers import SentenceTransformer
from .database import SessionLocal
from . import models

# 1. INITIALIZATION: Load the "brain" once when the worker starts
print("Loading Embedding Model (MiniLM-L6-v2)...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def process_claim_event(ch, method, properties, body):
    db = SessionLocal()
    try:
        claim_data = json.loads(body)
        claim_id = claim_data.get('id')
        text_to_process = claim_data.get('description', '')

        print(f" [x] AI Worker: Processing Claim {claim_id}")

        # 2. CHUNKING: For now, we treat the description as one chunk.
        # In the future, we can split longer PDFs here.
        
        # 3. EMBEDDING: Turn the text into 384 numbers
        vector_embedding = embedding_model.encode(text_to_process).tolist()

        # 4. UPSERTING: Save the chunk and its vector to Postgres
        new_chunk = models.DocumentChunk(
            claim_id=claim_id,
            content=text_to_process,
            embedding=vector_embedding
        )
        db.add(new_chunk)
        
        # Update claim status to 'Processed'
        db.query(models.Claim).filter(models.Claim.id == claim_id).update({"status": "Processed"})
        
        db.commit()
        print(f" [v] Success: Claim {claim_id} embedded and saved to pgvector.")

    except Exception as e:
        print(f" [!] AI Worker Error: {e}")
        db.rollback()
    finally:
        db.close()
        ch.basic_ack(delivery_tag=method.delivery_tag)

def start_worker():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='127.0.0.1'))
    channel = connection.channel()
    channel.queue_declare(queue='claims_queue', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='claims_queue', on_message_callback=process_claim_event)
    
    print(' [*] AI Worker is listening. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()
