import math
import json


class VectorStore:

    def __init__(self, chunks, embeddings):
        self.chunks = chunks
        self.embeddings = embeddings

    def get_total_vectors(self):
        return len(self.embeddings)

    def get_dimensions(self):

        if not self.embeddings:
            return 0

        return len(self.embeddings[0])

    def cosine_similarity(self, vector1, vector2):

        dot_product = sum(
            a * b for a, b in zip(vector1, vector2)
        )

        magnitude1 = math.sqrt(
            sum(a * a for a in vector1)
        )

        magnitude2 = math.sqrt(
            sum(b * b for b in vector2)
        )

        if magnitude1 == 0 or magnitude2 == 0:
            return 0

        return dot_product / (magnitude1 * magnitude2)

    # Search for similar chunks
    def search(self, query_embedding, top_k=2):

        scores = []

        for i, embedding in enumerate(self.embeddings):

            score = self.cosine_similarity(
                query_embedding,
                embedding
            )

            scores.append((i, score))

        scores.sort(
            key=lambda x: x[1],
            reverse=True
        )

        results = []

        for index, score in scores[:top_k]:

            chunk = self.chunks[index]

            # Support both old and new chunk formats
            if isinstance(chunk, dict):

                result = {
                    "text": chunk["text"],
                    "page": chunk.get("page"),
                    "score": score
                }

            else:

                result = {
                    "text": chunk,
                    "score": score
                }

            results.append(result)

        return results


def create_vector_store(chunks, embeddings):

    return VectorStore(chunks, embeddings)


def save_vector_store(store, file_path):

    data = {
        "chunks": store.chunks,
        "embeddings": store.embeddings
    }

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file)

    print("Vector Store Saved Successfully!")


def load_vector_store(file_path):

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    store = VectorStore(
        data["chunks"],
        data["embeddings"]
    )

    print("Vector Store Loaded Successfully!")

    return store