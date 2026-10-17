import ollama

response = ollama.embed(
    model='qllama/bge-reranker-v2-m3:latest',
    input='The sky is blue because of Rayleigh scattering',
)
print(response.embeddings)
