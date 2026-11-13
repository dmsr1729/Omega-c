from modules.llm import generate_answer

# Sample question
query = "What programming languages are mentioned?"

# Sample context
context = """
The candidate has experience with Java, Python, and SQL.
The candidate has also worked on web development projects.
"""

# Generate answer
answer = generate_answer(query, context)

# Display answer
print("User Question:", query)

print("\nGenerated Answer:")
print(answer)