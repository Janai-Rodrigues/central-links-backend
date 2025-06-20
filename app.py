from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
CORS(app) # Habilita CORS para todas as rotas

# Configuração do banco de dados
# O Render injeta a DATABASE_URL no ambiente, mas para testes locais,
# ou se preferir definir explicitamente, você pode usar a URL direta.
# Certifique-se de que a URL comece com 'postgresql://' se for 'postgres://' do Render
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'postgresql://cebtral_ferramentas_db_user:Sk02yJqBZ7ab2yZb2u3ogt5upuDWTmqj@dpg-d1acggumcj7s73fd5arg-a.oregon-postgres.render.com/cebtral_ferramentas_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo do Banco de Dados
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    url = db.Column(db.String(200), nullable=False)
    icon = db.Column(db.String(200), nullable=True) # Icone agora é opcional

    def __repr__(self):
        return f'<Link {self.name}>'

# Rota para servir imagens da pasta 'images'
@app.route('/api/images')
def get_images():
    images_dir = os.path.join(app.root_path, 'images')
    if not os.path.exists(images_dir):
        return jsonify({"error": "Images directory not found"}), 404

    try:
        image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
        # Filtra para incluir apenas arquivos de imagem comuns (png, jpg, jpeg, gif, ico)
        image_files = [f for f in image_files if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.ico'))]
        return jsonify(image_files)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Rota para servir uma imagem específica
@app.route('/images/<filename>')
def serve_image(filename):
    images_dir = os.path.join(app.root_path, 'images')
    return send_from_directory(images_dir, filename)

# Rota para obter todos os links (GET) e criar um novo link (POST)
@app.route('/api/links', methods=['GET', 'POST'])
def handle_links():
    if request.method == 'POST':
        # Criar um novo link
        data = request.get_json()
        if not data or not all(k in data for k in ['name', 'url']):
            return jsonify({"error": "Dados incompletos para o link"}), 400
        
        new_link = Link(
            name=data['name'],
            url=data['url'],
            icon=data.get('icon', None) # icon é opcional
        )
        db.session.add(new_link)
        db.session.commit()
        return jsonify({
            "id": new_link.id,
            "name": new_link.name,
            "url": new_link.url,
            "icon": new_link.icon
        }), 201 # 201 Created

    elif request.method == 'GET':
        # Obter todos os links
        links = Link.query.all()
        links_data = []
        for link in links:
            links_data.append({
                "id": link.id,
                "name": link.name,
                "url": link.url,
                "icon": link.icon
            })
        return jsonify(links_data)


# Rota para obter, atualizar ou excluir um link específico por ID
@app.route('/api/links/<int:link_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_link(link_id):
    link = Link.query.get_or_404(link_id) # Busca o link pelo ID, ou retorna 404

    if request.method == 'GET':
        # Obter um link específico
        return jsonify({
            "id": link.id,
            "name": link.name,
            "url": link.url,
            "icon": link.icon
        })

    elif request.method == 'PUT':
        # Atualizar um link existente
        data = request.get_json()
        if not data:
            return jsonify({"error": "Nenhum dado fornecido para atualização"}), 400

        link.name = data.get('name', link.name)
        link.url = data.get('url', link.url)
        link.icon = data.get('icon', link.icon)
        
        db.session.commit()
        return jsonify({
            "id": link.id,
            "name": link.name,
            "url": link.url,
            "icon": link.icon
        })

    elif request.method == 'DELETE':
        # Excluir um link
        db.session.delete(link)
        db.session.commit()
        return jsonify({"message": "Link excluído com sucesso"}), 204 # 204 No Content

# Rota de teste
@app.route('/')
def home():
    return "Backend da Central de Links está funcionando!"

if __name__ == '__main__':
    app.run(debug=True)