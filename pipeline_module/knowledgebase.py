import csv
import os
import uuid
from transformers import BertModel, BertTokenizer
import torch
from sklearn.neighbors import NearestNeighbors
import numpy as np
import joblib

class NLR2KnowledgeBase:
    def __init__(self, csv_path='../config_file/nlr2s.csv', knn_model_path='../config_file/knn_model.pkl', k=5):
        self.csv_path = csv_path
        self.knn_model_path = knn_model_path
        self.nlr2_texts = []
        self.groups = []
        self.ids = []
        self.k = k
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.model = BertModel.from_pretrained('bert-base-uncased')
        self.neigh = NearestNeighbors(n_neighbors=k, metric='euclidean')
        self._load_knowledge_base()
        self._load_knn_model()

    def _embed(self, text):
        inputs = self.tokenizer(text, return_tensors='pt')
        outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).detach().numpy().tolist()

    def _load_knowledge_base(self):
        if os.path.exists(self.csv_path):
            with open(self.csv_path, mode='r', newline='', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                for row in reader:
                    self.ids.append(row[0])
                    self.nlr2_texts.append(row[1])
                    self.groups.append(row[2])

    def _save_knowledge_base(self):
        with open(self.csv_path, mode='w', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file)
            for id, text, group in zip(self.ids, self.nlr2_texts, self.groups):
                writer.writerow([id, text, group])

    def _load_knn_model(self):
        if os.path.exists(self.knn_model_path):
            self.neigh = joblib.load(self.knn_model_path)
        elif self.ids:  # Ensure there's data to fit the model if creating it new
            self._update_neighbors()

    def _save_knn_model(self):
        joblib.dump(self.neigh, self.knn_model_path)

    def add_nlr2(self, nlr2_text, group="Uncategorized"):
        id = str(uuid.uuid4())
        embedding = self._embed(nlr2_text)
        self.ids.append(id)
        self.nlr2_texts.append(nlr2_text)
        self.groups.append(group)
        self.embeddings.append(embedding)
        self._save_knowledge_base()
        self._update_neighbors()

    def _update_neighbors(self):
        if len(self.embeddings) > 1:
            embeddings_matrix = np.array(self.embeddings)
            self.neigh.fit(embeddings_matrix)
            self._save_knn_model()
            
    def find_neighbors(self, target_embedding):
        distances, indices = self.neigh.kneighbors([target_embedding])
        return distances, indices