from sentence_transformers import SentenceTransformer
import numpy as np
import json

# Load JSON
print("Loading Json...")
with open('/Users/aosiqiao/Desktop/research_data.json', 'r') as f:
    data = json.load(f)

print(f"Loaded {len(data)} records from research_data.json.")

# Initialize the model
print("Initializing the embedding model...")
model = SentenceTransformer('all-MiniLM-L6-v2')

# Create embeddings
texts = [item['content'] for item in data]
print(f"Generating embeddings for {len(texts)} texts...")
embeddings = model.encode(texts)

# Save embeddings
print("Saving embeddings.npy and texts.json...")
np.save('/Users/aosiqiao/Desktop/Coding/embeddings.npy', embeddings)
with open('/Users/aosiqiao/Desktop/Coding/texts.json', 'w') as f:
    json.dump(texts, f)

print("Embeddings saved")
