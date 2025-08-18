
import re
import json
import numpy as np
from ollama import Client, EmbedResponse




class Embedder:

    def __init__(
        self,
        txt_file_path: str,
        chunks_output_path: str,
        embeds_output_path: str,
        ollama_model: str = "mxbai-embed-large",
        ollama_host: str = "http://localhost:11434"
    ) -> None:
        self.__txt_file_path = txt_file_path
        self.__chunks_output_path = chunks_output_path
        self.__embeds_output_path = embeds_output_path
        self.__ollama_model = ollama_model
        self.__ollama_host = ollama_host


    def __ollama_embed_client(self, text_input) -> EmbedResponse:
        return Client(
            host = self.__ollama_host
        ).embed(
            model = self.__ollama_model,
            input = text_input
        )


    def __cat_n(self, lst, n, sep = ". ") -> list:
        ret = []
        for i in range(0, len(lst), n):
            ret.append(sep.join(lst[i:i+n]))
        return ret


    def __clean_process_recombine(self, txt, n_sent, rem_char_len = None, verbose = False) -> str:
        ## Split into sentences:
        txt_sent = re.split(r"[.?!]\s", txt)
        ## Remove any new-line chars:
        txt_sent = [s.replace("\n", "") for s in txt_sent]
        ## Remove empty:
        txt_sent = [s for s in txt_sent if s != ""]
        ## Remove sentences shorter than N len:
        if rem_char_len:
            txt_sent = [s for s in txt_sent if len(s) >= rem_char_len]
        ## Combine every N-Sentences into a new paragraph:
        txt_para = self.__cat_n(txt_sent, n = n_sent)
        if verbose:
            print(f"{len(txt_para)} paragraphs created")
        ## return:
        # return "\n\n".join(txt_para)
        return txt_para


    def embed_txt_doc(
        self,
        chunk_para: bool = True,
        n_sent: int = 4,
        rem_char_len: bool = None,
        return_embeds: bool = False
    ) -> EmbedResponse:

        ## Load .txt data:
        with open(self.__txt_file_path, "r") as f:
            txt_data = f.read()

        ## Chunk data & save output:
        if chunk_para:
            txt_data = re.split(r"\n\n", txt_data)
            txt_data = [t for t in txt_data if t != ""]
        else:
            txt_data = self.__clean_process_recombine(
                txt = txt_data,
                n_sent = n_sent,
                rem_char_len = rem_char_len
            )
        with open(self.__chunks_output_path, "w", encoding = "utf-8") as f:
            json.dump(txt_data, f, ensure_ascii = False, indent = 4)
            print(f"|----- Chunks of length {len(txt_data)} created & saved to {self.__chunks_output_path}")

        ## Embed data & save output:
        print("|----- Creating embeddings...")
        embeddings = self.__ollama_embed_client(text_input = txt_data).embeddings
        with open(self.__embeds_output_path, "w", encoding = "utf-8") as f:
            json.dump(embeddings, f, ensure_ascii = False, indent = 4)
            print(f"|----- Embeddings of length {len(embeddings)} created & saved to {self.__embeds_output_path}")
        return embeddings if return_embeds else None
