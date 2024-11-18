 
import buscarml.config as config
import os
import pandas as pd
from PIL import Image
from tqdm import tqdm
import numpy as np
from annoy import AnnoyIndex
from tqdm import tqdm
from tensorflow.keras.preprocessing import image
from azure.storage.blob import BlobServiceClient
 
from tensorflow.keras.applications.densenet import DenseNet201, preprocess_input
 
from tensorflow.keras.applications.xception import Xception
from tensorflow.keras.applications.xception import preprocess_input 
from tensorflow.keras.models import Model
import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)

class LoadData:
    """Loading the data from Single/Multiple Folders or form CSV file"""
    def __init__(self):
        pass
 
class FeatureExtractor:
    def __init__(self):
 
       base_model = DenseNet201(weights='imagenet', include_top=True)
 
       self.model = Model(inputs=base_model.input, outputs=base_model.get_layer('avg_pool').output)
    def extract(self, img):
        # Tamaño de la imagen
        img = img.resize((224, 224))
 
        # Convertimos a color
        img = img.convert('RGB')
        # Reformateamos la imagen
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        # Extraemos las características
        feature = self.model.predict(x)[0]
        return feature / np.linalg.norm(feature)
    
    def get_feature(self,image_data:list):
        self.image_data = image_data 
        #fe = FeatureExtractor()
        features = []
        for img_path in tqdm(self.image_data):  
            # Iteramos y extraemos las características
            try:
                feature = self.extract(img=Image.open(img_path))
                features.append(feature)
            except:
                features.append(None)
                continue
        return features

class Index:
    def __init__(self,image_list:list):
        self.image_list = image_list
        if 'meta-data-files' not in os.listdir():
            os.makedirs("meta-data-files")
        self.FE = FeatureExtractor()
    def start_feature_extraction(self):
        image_data = pd.DataFrame()
        image_data['images_paths'] = self.image_list
        f_data = self.FE.get_feature(self.image_list)
        image_data['features']  = f_data
        image_data = image_data.dropna().reset_index(drop=True)
        image_data.to_pickle(config.image_data_with_features_pkl)
        print("Image Meta Information Saved: [meta-data-files/image_data_features.pkl]")
        return image_data
    def start_indexing(self,image_data):
        self.image_data = image_data
        f = len(image_data['features'][0]) # 
        f = len(self.image_data.loc[0, 'features'])
        t = AnnoyIndex(f, 'euclidean')
        for i, v in tqdm(zip(self.image_data.index, image_data['features'])):
            t.add_item(i, v)
        t.build(500)  # 100 arboles
        print("Saved the Indexed File:"+"[meta-data-files/image_features_vectors.ann]")
        t.save(config.image_features_vectors_ann)
    def start(self):
        if len(os.listdir("meta-data-files/"))==0:
            data = self.start_feature_extraction()
            self.start_indexing(data)
        else:
            print("Metadata and Features are allready present, Do you want Extract Again? Enter yes or no")
            flag  = str(input())
            if flag.lower() == 'yes':
                data = self.start_feature_extraction()
                self.start_indexing(data)
            else:
                print("Meta data allready Present, Please Apply Search!")
                print(os.listdir("meta-data-files/"))

class SearchImage:
    def __init__(self):
        self.image_data = pd.read_pickle(config.image_data_with_features_pkl)
        self.f = len(self.image_data.loc[0, 'features']) 
    def search_by_vector(self,v,n:int):
        self.v = v  
        self.n = n  
        u = AnnoyIndex(self.f, 'euclidean')
        u.load(config.image_features_vectors_ann)  
        index_list = u.get_nns_by_vector(self.v, self.n)  
        return dict(zip(index_list,self.image_data.iloc[index_list]['images_paths'].to_list()))
    def get_query_vector(self,img:Image.Image):
        #self.image_path = image_path
        #img = Image.open(self.image_path)
        fe = FeatureExtractor()
        query_vector = fe.extract(img)
        return query_vector
    def find_most_similar_image(self, img: Image.Image):
        query_vector = self.get_query_vector(img)
        u = AnnoyIndex(self.f, 'euclidean')
        u.load(config.image_features_vectors_ann)

        n_images = 1
        index_list, distances = u.get_nns_by_vector(query_vector, n_images, include_distances=True)

        img_list = list(self.image_data.iloc[index_list]['images_paths'].to_list())
    # Obtener la ruta de la imagen más similar
        most_similar_image_path = img_list[0]
        print("ruta",most_similar_image_path)
    # Añadir la carpeta "images" a la ruta


         # Añadir solo el nombre del archivo a la ruta
        file_name = os.path.basename(most_similar_image_path)
 
        return file_name