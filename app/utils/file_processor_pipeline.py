from langchain_text_splitters import CharacterTextSplitter
from langchain_community.document_loaders import TextLoader, PyPDFLoader

from sentence_transformers import SentenceTransformer

import pandas as pd
import numpy as np
import faiss
import os

class FileProcessorPipeline:
    def __init__(self, input_path, output_path, embedding_model_name):

        self.input_path = input_path
        self.output_path = output_path

        self.embedding_model = SentenceTransformer(embedding_model_name)

        self.work_format = ["pdf", "txt"]

    def check_format(self, file_path):
        for form in self.work_format:
            if file_path.endswith(form):
                return form
        return None

    def load_text(self):
        docs_source = {}

        for file_name in os.listdir(self.input_path):
            try:
                file_format = self.check_format(file_name)
                if file_format is None:
                    continue
                print(f"Reading file: {file_name}...")
                if file_format == "pdf":
                    loader = PyPDFLoader(os.path.join(self.input_path, file_name))
                elif file_format == "txt":
                    loader = TextLoader(os.path.join(self.input_path, file_name), autodetect_encoding=True)

                docs = loader.load()
                file_text = " ".join([doc.page_content for doc in docs if len(doc.page_content) > 0])

                if len(file_text) > 0:
                    docs_source[file_name.split(".")[0]] = file_text
                    print("Success")
                else:
                    print("Fail")
            except Exception as ex:
                print(f"Error with file: {file_name}. Error -> {ex}")

        if len(docs_source) == 0:
            return None
        return docs_source

    def chunking(self, docs_source):

        text_splitter = CharacterTextSplitter(
            separator="\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        d_chunks = {}

        for topic, text in docs_source.items():
            print(f"Chunking topic: {topic}...")
            chunks = text_splitter.split_text(text)
            d_chunks[topic] = chunks
            print(f"Number of chunk: {len(chunks)}")

        return d_chunks

    def create_vectors_db(self, docs_chunk):

        docs_embs = {}
        d_chunks = {"chunk": [], "domen": []}

        for topic, chunks in docs_chunk.items():
            print(f"Vectorization {topic}...")
            arr_embs = []
            for chunk in chunks:
                arr_embs.append(self.embedding_model.encode([chunk])[0])
                d_chunks['domen'].append(topic)
                d_chunks['chunk'].append(chunk)

            docs_embs[topic] = np.array(arr_embs)

        for topic, embs in docs_embs.items():
            d = embs.shape[1]
            index = faiss.IndexFlatL2(d)
            faiss.normalize_L2(embs)
            index.add(embs)
            faiss.write_index(index, os.path.join(self.output_path, f"{topic}.index"))

        df = pd.DataFrame(d_chunks)
        df.to_csv(os.path.join(self.output_path, "all_data.csv"), index=False)

        return df

    def start_process(self):

        d_source = self.load_text()

        if d_source is None:
            print("Nothing correct files (load_text process).")
            return False

        d_chunks = self.chunking(d_source)

        df_res = self.create_vectors_db(d_chunks)

        return df_res


def generate_descriptions_for_dones(df: pd.DataFrame, model):

    domens = df['domen'].unique()

    d_description = {"descriptions": "", "domens": list(domens) + ["chitchat"]}

    for domen in domens:
        df_tmp = df[df['domen'] == domen]

        i = 0
        text = ""
        while len(text) < 10000 and i < len(df_tmp):
            text += df_tmp.iloc[i]['chunk']
            i += 1

        prompt = f"""Напиши в 2-3 коротких предложениях, в чем тема этого текста. Пиши на том языке, котором сам текст. 
        Не пиши ничего лишнего, только 1-2 коротких предложениях 
        Текст: {text}"""

        result = model.invoke(prompt)

        d_description["descriptions"] += domen + " - " + result.content + "\n"

    d_description["descriptions"] += "chitchat - сообщение, которое ни относится ни к одному из вышеперечисленных классов"
    print(f"Описание каждого класса: {d_description['descriptions']}")
    return d_description

