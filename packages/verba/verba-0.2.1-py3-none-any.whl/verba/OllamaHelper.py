import os
import json
import time
import numpy as np
import pandas as pd
from ollama import Client
from pdfminer.high_level import extract_pages



class Ragby:

    def __init__(self, chat_model, embedding_model, top_n = 10, ollama_client = None, data_dir = None):
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        self.top_n = top_n
        self.ollama_client = Client(host = "http://localhost:11434") if ollama_client is None else ollama_client
        self.data_dir = "data" if data_dir is None else data_dir
        self.__setup_dirs()


    def __repr__(self):
        return f"Ragby(chat_model={self.chat_model}, embedding_model={self.embedding_model}, top_n={self.top_n}, ollama_client={self.ollama_client})"


    def __setup_dirs(self):
        if "chunks" not in os.listdir():
            print("--- Creating 'chunks' folder")
            os.mkdir("chunks")
        if "embeddings" not in os.listdir():
            print("--- Creating 'embeddings' folder")
            os.mkdir("embeddings")

    
    def make_chunks(self, file_name, paragraphs = False):
        file_name_prefix = file_name.split(".")[0]
        data_file_path = f"{self.data_dir}/{file_name}"
        if paragraphs:
            with open(data_file_path, "r") as f:
                chunks = []
                buffer = []
                for line in f.readlines():
                    line = line.strip()
                    if line:
                        buffer.append(line)
                    elif len(buffer):
                        chunks.append(" ".join(buffer))
                        buffer = []
                if len(buffer):
                    chunks.append(" ".join(buffer))
        else:
            with open(data_file_path, "r") as f:
                chunks = f.read().splitlines()
        with open(f"chunks/{file_name_prefix}.json", "w") as f:
            json.dump(chunks, f)
            print(f"--- Created chunks of length: {len(chunks)}")
            print(f"--- Chunks stored in 'chunks/{file_name_prefix}.json'")
            return [chunks, f"chunks/{file_name_prefix}.json"]


    def make_chunks_pdf(self, file_name):
        file_name_prefix = file_name.split(".")[0]
        data_file_path = f"{self.data_dir}/{file_name}"
        pdf_elements = []
        for page_layout in extract_pages(data_file_path):
            for element in page_layout:
                pdf_elements.append(element)
        text_pdf_elements = [e for e in pdf_elements if str(type(e)) == "<class 'pdfminer.layout.LTTextBoxHorizontal'>"]
        text_pdf_elements = [e.get_text().strip() for e in text_pdf_elements]
        with open(f"chunks/{file_name_prefix}.json", "w") as f:
            json.dump(text_pdf_elements, f)
            print(f"--- Created chunks of length: {len(text_pdf_elements)}")
            print(f"--- Chunks stored in 'chunks/{file_name_prefix}.json'")
            return [text_pdf_elements, f"chunks/{file_name_prefix}.json"]


    def make_n_chunks(self, file_name, n = 1):
        file_name_prefix = file_name.split(".")[0]
        data_file_path = f"{self.data_dir}/{file_name}"
        with open(data_file_path, "r") as f:
            chunks = f.read().splitlines()
            chunks = [c for c in chunks if c != ""]
            chunks = [chunks[x:x + n] for x in range(0, len(chunks), n)]
            chunks = [" ".join(nc) for nc in chunks]
        with open(f"chunks/{file_name_prefix}.json", "w") as f:
            json.dump(chunks, f)
            print(f"--- Created chunks of length: {len(chunks)}")
            print(f"--- Each chunk contains {n} sub-chunks")
            print(f"--- Chunks stored in 'chunks/{file_name_prefix}.json'")
            return [chunks, f"chunks/{file_name_prefix}.json"]


    def make_n_chunks_return(self, text, n, split_by = None):
        chunks = [t.strip() for t in text.split(split_by)]
        chunks = [chunks[x:x + n] for x in range(0, len(chunks), n)]
        chunks = [" ".join(nc) for nc in chunks]
        return chunks

    
    def make_embeddings_return(self, c):
        if isinstance(c, list):
            return [self.ollama_client.embeddings(model = self.embedding_model, prompt = chunk)["embedding"] for chunk in c]
        elif isinstance(c, str):
            return self.ollama_client.embeddings(model = self.embedding_model, prompt = c)["embedding"]
        else:
            raise ValueError("Input to 'c' must be a string (str) or a list of strings (list[str])")

    
    def make_embeddings(self, c, file_name):
        file_name_prefix = file_name.split(".")[0]
        emb = [self.ollama_client.embeddings(model = self.embedding_model, prompt = chunk)["embedding"] for chunk in c]
        with open(f"embeddings/{file_name_prefix}.json", "w") as f:
            json.dump(emb, f)
            print(f"--- Created embeddings of length: {len(emb)}")
            print(f"--- Embeddings stored in 'embeddings/{file_name_prefix}.json'")
            return f"embeddings/{file_name_prefix}.json"
    
    
    def cosine_similarity(self, x, y_arr):
        x_norm = np.linalg.norm(x)
        return [np.dot(x, y) / (x_norm * np.linalg.norm(y)) for y in y_arr]
    
    
    def get_embedding_similarity(self, sim_score_list, text_chunks):
        sorted_sim_scores = sorted(zip(sim_score_list, range(len(sim_score_list))), reverse = True)
        return [text_chunks[sss[1]] for sss in sorted_sim_scores[:self.top_n]]
    
    
    def make_chat_message(self, user_prompt, system_prompt, text_chunks_path, text_embeddings_path):
        with open(text_embeddings_path, "r") as f:
            text_embeddings = json.load(f)
        with open(text_chunks_path, "r") as f:
            text_chunks = json.load(f)
        prompt_embedding = self.ollama_client.embeddings(model = self.embedding_model, prompt = user_prompt)["embedding"]
        sim_scores = self.cosine_similarity(prompt_embedding, text_embeddings)
        similar_chunks = self.get_embedding_similarity(sim_scores, text_chunks)
        system_content = system_prompt + "\n".join(similar_chunks)
        return [
            {
                "role": "system",
                "content": system_content
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ]
    
    
    def chat(self, user_prompt, system_prompt, text_chunks_path, text_embeddings_path):
        chat_messages = self.make_chat_message(
            user_prompt = user_prompt, 
            system_prompt = system_prompt, 
            text_chunks_path = text_chunks_path, 
            text_embeddings_path = text_embeddings_path
        )
        response = self.ollama_client.chat(
            model = self.chat_model,
            messages = chat_messages
        )
        return response["message"]["content"]
