
import re
import json
import numpy as np
from ollama import Client, EmbedResponse




class Generator():

    def __init__(
        self,
        chunk_file_path: str,
        embed_file_path: str,
        ollama_model: str = "mxbai-embed-large",
        ollama_host: str = "http://localhost:11434"
    ) -> None:
        self.__ollama_model = ollama_model
        self.__ollama_host = ollama_host
        self.__chunk_file_path = chunk_file_path
        with open(self.__chunk_file_path, "r") as f:
            self.__chunks = json.load(f)
        self.__embed_file_path = embed_file_path
        with open(self.__embed_file_path, "r") as f:
            self.__embeds = json.load(f)


    def __ollama_embed_client(self, text_input) -> EmbedResponse:
        return Client(
            host = self.__ollama_host
        ).embed(
            model = self.__ollama_model,
            input = text_input
        )


    def __embed(self, text_input) -> EmbedResponse:
        oec = self.__ollama_embed_client(text_input = text_input)
        return oec.embeddings[0]


    def __cosine_similarity(self, x, y_arr) -> list:
        x_norm = np.linalg.norm(x)
        return [np.dot(x, y) / (x_norm * np.linalg.norm(y)) for y in y_arr]


    def __get_top_chunks(self, sim_score_list, text_chunks, top_n, dev_mode) -> str:
        sorted_sim_scores = sorted(zip(sim_score_list, range(len(sim_score_list))), reverse = True)
        ret = [text_chunks[sss[1]] for sss in sorted_sim_scores[:top_n]]
        if dev_mode:
            return "\n\n".join(ret)
        else:
            ret = " ".join(ret)
            ret = ret.replace("\n", "")
            return ret


    def generate(self, prompt: str, top_n: int = 4, dev_mode: bool = False) -> str:
        prompt_embed = self.__embed(prompt)
        cos_sim = self.__cosine_similarity(prompt_embed, self.__embeds)
        most_similar_chunks = self.__get_top_chunks(cos_sim, self.__chunks, top_n = top_n, dev_mode = dev_mode)
        return most_similar_chunks
