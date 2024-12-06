from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import json
from sentence_transformers import SentenceTransformer
import faiss
import openai
import os
import nltk
import traceback

# Initialize Flask
app = Flask(__name__)
CORS(app)  # Enable CORS

# Suppress parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY") 
if not openai.api_key:
    raise EnvironmentError("OpenAI API key not set.")

# Download NLTK
nltk.download('punkt')

# Load embeddings and text data
try:
    embeddings = np.load('/Users/aosiqiao/Desktop/Coding/embeddings.npy')
    with open('/Users/aosiqiao/Desktop/Coding/texts.json', 'r') as f:
        texts = json.load(f)
except Exception as e:
    raise FileNotFoundError(f"Error loading data files: {e}")

# Initialize FAISS index for search
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# Search for the most relevant sentences
def search_with_sources(query, top_k=10, relevance_threshold=1.8):
    """Search for the most relevant text, extract sentences, and indicate source information."""
    model = SentenceTransformer('all-MiniLM-L6-v2')
    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, top_k)

    results = []
    for idx in indices[0]:
        if distances[0][0] >= relevance_threshold:
            continue

        article_content = texts[idx]
        source = f"Article {idx + 1}"
        
        sentences = nltk.sent_tokenize(article_content)
        sentence_embeddings = model.encode(sentences)
        
        sentence_index = faiss.IndexFlatL2(sentence_embeddings.shape[1])
        sentence_index.add(sentence_embeddings)

        distances_to_query, sentence_indices = sentence_index.search(np.array([query_embedding[0]]), len(sentences))
        top_sentences = [sentences[i] for i in sentence_indices[0][:3]] 

        results.append({
            "content": article_content,
            "source": source,
            "sentences": top_sentences
        })

    return results

# This is for generating a response from OpenAI GPT!
def generate_response(context, user_query):
    """Generate a response from GPT based on the given context and query."""
    try:
        truncated_context = context[:3000]  # Truncate to avoid token limit
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Context: {truncated_context}\n\nQuestion: {user_query}"}
            ]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"Error generating response: {e}"

# API for Chatbot
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        print("Received data:", data)
        user_query = data.get('query')

        if not user_query:
            return jsonify({"error": "No query"}), 400

        # Retrieve context a
        results = search_with_sources(user_query, top_k=10)
        print("Search results:", results)  

        if results:
            context = results[0]["content"]
            source = results[0]["source"]
            relevant_sentences = results[0]["sentences"]
            combined_context = " ".join(relevant_sentences)
            reply = generate_response(combined_context, user_query)

            print("Generated reply:", reply)
            print("Relevant sentences:", relevant_sentences)

            return jsonify({
                "reply": reply,
                "source": {
                    "article": source,
                    "sentences": relevant_sentences
                }
            })
        else:
            print("No relevant context")
            return jsonify({"reply": "No relevant context"}), 404
    except Exception as e:
        print(f"Error in /chat route: {e}")
        traceback.print_exc()  
        return jsonify({"error": str(e)}), 500

# Run the app locally
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)  
