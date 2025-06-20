import os
from flask import Flask, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

# Configuração do Banco de Dados
# Render usa 'postgresql://', mas SQLAlchemy para psycopg2 precisa de 'postgresql+psycopg2://'
# ou apenas 'postgresql://' com a versão correta do SQLAlchemy/psycopg2.
# Para compatibilidade, vamos garantir que a URL comece com 'postgresql://' se for o caso.
# A Render já fornece a URL no formato correto para SQLAlchemy, então o .replace() pode não ser necessário
# dependendo da sua versão de SQLAlchemy e psycopg2.
# Manteremos a lógica de substituição para garantir compatibilidade com exemplos anteriores,
# mas se der erro no deploy, pode ser a primeira coisa a remover.
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith("postgresql://"):
    # SQLAlchemy 1.4+ e 2.0+ com psycopg2 normalmente aceitam postgresql://
    # Se você tiver problemas, pode tentar:
    # app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # URL para desenvolvimento local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/central_links' # Adapte para seu DB local
    print("AVISO: Usando URL de banco de dados local. Certifique-se de definir DATABASE_URL no Render.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
CORS(app) # Habilita CORS para todas as rotas


# --- NOVO CÓDIGO: CRIAR TABELAS AO INICIAR O APP ---
# Este bloco garantirá que as tabelas sejam criadas no banco de dados
# quando o aplicativo iniciar no Render, caso ainda não existam.
with app.app_context():
    db.create_all()
    print(">>> Tabelas verificadas/criadas no banco de dados.")
# --------------------------------------------------


# Definição do Modelo do Banco de Dados
class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(255), nullable=True) # Nome do arquivo do ícone (ex: 'icone1.png')

    def __repr__(self):
        return f'<Link {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'icon': self.icon
        }

# Rotas da API

# Rota para servir imagens de ícones
@app.route('/images/<path:filename>')
def serve_image(filename):
    # Certifique-se de que 'images' é a pasta onde você armazena seus ícones no backend
    return send_from_directory('images', filename)

# Rota para listar todos os nomes de arquivos de imagem disponíveis
@app.route('/api/images', methods=['GET'])
def list_images():
    images_dir = os.path.join(app.root_path, 'images')
    if not os.path.exists(images_dir):
        return jsonify([])
    image_files = [f for f in os.listdir(images_dir) if os.path.isfile(os.path.join(images_dir, f))]
    return jsonify(image_files)


# Rota para adicionar um novo link (POST) e obter todos os links (GET)
@app.route('/api/links', methods=['GET', 'POST'])
def handle_links():
    if request.method == 'POST':
        data = request.get_json()
        new_link = Link(name=data['name'], url=data['url'], icon=data.get('icon'))
        db.session.add(new_link)
        db.session.commit()
        return jsonify(new_link.to_dict()), 201
    elif request.method == 'GET':
        links = Link.query.all()
        return jsonify([link.to_dict() for link in links])

# Rota para gerenciar um link específico por ID (GET, PUT, DELETE)
@app.route('/api/links/<int:link_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_single_link(link_id):
    link = Link.query.get_or_404(link_id)

    if request.method == 'GET':
        return jsonify(link.to_dict())
    elif request.method == 'PUT':
        data = request.get_json()
        link.name = data.get('name', link.name)
        link.url = data.get('url', link.url)
        link.icon = data.get('icon', link.icon)
        db.session.commit()
        return jsonify(link.to_dict())
    elif request.method == 'DELETE':
        db.session.delete(link)
        db.session.commit()
        return jsonify({'message': 'Link excluído com sucesso'}), 200

# Rota Home
@app.route('/')
def home():
    return "Backend da Central de Links está rodando!" # Mensagem simples para verificar se o backend está ativo

if __name__ == '__main__':
    # Este bloco só é executado quando você roda app.py diretamente (localmente)
    # No Render, o servidor web (gunicorn) inicia o app de outra forma.
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 5000))