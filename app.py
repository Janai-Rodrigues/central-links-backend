import os
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas. Em produção, você pode restringir mais.

# Define o diretório onde as imagens estão
# O ideal é que 'images' esteja no mesmo nível do 'app.py' quando o backend for hospedado
IMAGES_DIR = 'images'

# Cria o diretório de imagens se ele não existir
if not os.path.exists(IMAGES_DIR):
    os.makedirs(IMAGES_DIR)

@app.route('/api/images', methods=['GET'])
def list_images():
    """
    Lista todos os arquivos de imagem no diretório IMAGES_DIR
    e retorna suas URLs relativas.
    """
    image_files = []
    # Lista arquivos e filtra por extensões comuns de imagem
    for filename in os.listdir(IMAGES_DIR):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico', '.webp', '.svg')):
            # Retorna o nome do arquivo, a URL completa será montada no frontend
            # ou o backend pode servir diretamente, dependendo da configuração de deploy.
            image_files.append(filename)
    return jsonify(image_files)

@app.route('/images/<path:filename>')
def serve_image(filename):
    """
    Serve arquivos estáticos do diretório IMAGES_DIR.
    """
    return send_from_directory(IMAGES_DIR, filename)

if __name__ == '__main__':
    # Em ambiente de desenvolvimento, execute com debug=True
    # Em produção, você usará um servidor WSGI como Gunicorn.
    app.run(debug=True, port=5000) # O backend rodará na porta 5000 por padrão