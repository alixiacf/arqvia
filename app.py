from flask import Flask, Response, request, render_template, jsonify, send_file
from flask_cors import CORS
import base64
import tempfile
import os
from PIL import Image
from io import BytesIO
from buscarml.buscarml import Index, LoadData, SearchImage
import io
from azure.storage.blob import BlobServiceClient

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def get_message():
    # Función para la ruta raíz que renderiza el archivo index.html
    print("Got request in main function")
    return render_template("./index.html")

@app.route('/upload_static_file', methods=['POST'])
def upload_static_file():
    # Función para manejar la carga de imágenes estáticas
    # Obtener la imagen en formato base64 del JSON recibido
    data = request.get_json()
    image_base64 = data['image']
    print("image_base64") 

    # Eliminar la parte "data:image/png;base64," si está presente
    header, image_base64 = image_base64.split(';base64,')
    
    # Decodificar la imagen base64
    image_data = base64.b64decode(image_base64)
    print("imagen_decodificada")
    
    # Cargar la imagen decodificada en un objeto Image y convertirla a PNG
    input_image = Image.open(BytesIO(image_data))
    output_image = input_image.convert('RGBA')
    print("imagen convertida")

    # Eliminar las variables no utilizadas
    del data
    del input_image

    # Realizar la búsqueda de la imagen más similar
    search_image = SearchImage()
    most_similar_image_path = search_image.find_most_similar_image(output_image)

    cam_digit = most_similar_image_path.split("_")[1][3]
    degrees_digit = int(most_similar_image_path.split("_")[1][6:8]) * 15
    print("Grados convertidos:", degrees_digit)
    print("Número de cámara:", cam_digit)
    
    if (degrees_digit == 360):
        degrees_digit = 0
    degrees_digit = degrees_digit 
    print("Grados:", degrees_digit)

    file_name = f"pan{cam_digit}.jpg"
    
    # Obtener la posición de la cámara en la panorámica
    position = f"0 {degrees_digit}  0"
    print(position)
    
    # Guardar la imagen convertida en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as temp_file:
        output_image.save(temp_file.name)
    del output_image

    # Devolver la ruta relativa de la imagen más similar como respuesta al cliente
    return jsonify({'temp_file': file_name, "position_name": position})

@app.route('/display_image.html')
def display_image():
    # Función para mostrar la imagen cargada
    file_name = request.args.get('file_name')
    position = request.args.get("position_name")  
    
    # Reemplazar '<connection_string>' con la cadena de conexión de tu cuenta de almacenamiento
    connection_string = "" 
    container_name = "castro"

    # Descargar la imagen del contenedor Blob
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(file_name)

    # Crear un objeto de archivo en memoria
    image_stream = io.BytesIO()
    data = blob_client.download_blob()
    data.readinto(image_stream)

    # Reiniciar el puntero del objeto de archivo en memoria
    image_stream.seek(0)

    # Transmitir la imagen a través del servidor
    # return send_file(image_stream, mimetype='image/png')
    
    # Renderizar la plantilla HTML con el nombre de la imagen y la posición como contexto
    return render_template('display_image.html', temp_file=file_name, position_name=position)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)