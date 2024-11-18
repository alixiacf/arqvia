# ArQVIA
**VSLAM Positioning Through Synthetic Data and Deep Learning: Applications in Virtual Archaeology**
[paper code] https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4633621

ArQVIA es una aplicación que utiliza posicionamiento VSLAM mediante datos sintéticos y aprendizaje profundo para resolver problemas de arqueología virtual.

## Características
- Procesamiento de datos posicionamiento con aprendizaje profundo.
- Aplicaciones en arqueología virtual.
- Implementación fácil con requisitos definidos en `requirements.txt`.

## Requisitos
Para ejecutar esta aplicación, necesitas instalar las dependencias listadas en `requirements.txt`.

### Instalación
1. Clona este repositorio:
   ```bash
   git clone https://github.com/alixiacf/arqvia.git
   cd arqvia

python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt


python app.py

Está configurado para usar azure BlobServiceClient, necesitarías una clave del servicio para implementar tu propia solucion.
