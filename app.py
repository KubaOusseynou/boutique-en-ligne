import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.utils import secure_filename

# Configurer l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'static/images'  # Dossier où les images seront stockées
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}  # Extensions autorisées
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 Mo

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Modèle pour les produits
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    prix = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)


@app.route('/')
def index():
    produits = Produit.query.all()
    return render_template('home.html', produits=produits)


@app.route('/admin')
def admin():
    produits = Produit.query.all()
    return render_template('admin.html', produits=produits)


def allowed_file(filename):
    """Vérifie si l'extension du fichier est autorisée."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


@app.route('/ajouter', methods=['POST'])
def ajouter_produit():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = float(request.form['prix'])
        stock = int(request.form['stock'])

        # Vérification et traitement du fichier image
        image = request.files.get('image')
        image_url = None
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)  # Sécuriser le nom du fichier
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image.save(image_path)
            image_url = f'/static/images/{filename}'  # L'URL relative de l'image

        # Créer le nouveau produit avec l'URL de l'image
        nouveau_produit = Produit(nom=nom, description=description, prix=prix, stock=stock, image_url=image_url)
        db.session.add(nouveau_produit)
        db.session.commit()

        return redirect(url_for('admin'))


@app.route('/supprimer/<int:id>', methods=['GET'])
def supprimer_produit(id):
    produit = Produit.query.get_or_404(id)
    db.session.delete(produit)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/modifier/<int:id>')
def modifier_produit_page(id):
    produit = Produit.query.get(id)
    produits = Produit.query.all()
    return render_template('admin.html', produits=produits, produit_modifie=produit)


@app.route('/modifier/<int:id>', methods=['POST'])
def modifier_produit(id):
    produit = Produit.query.get(id)
    if not produit:
        return "Produit introuvable", 404

    produit.nom = request.form['nom']
    produit.description = request.form['description']
    produit.prix = request.form['prix']
    produit.stock = request.form['stock']
    #produit.image_url = request.form['image_url']
    # Gestion de l'image
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            produit.image_url = f'/static/images/{filename}'

    try:
        db.session.commit()
        return redirect(url_for('admin'))
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de la modification : {e}", 500


if __name__ == '__main__':
    # Créer la base de données si elle n'existe pas
    with app.app_context():
        db.create_all()
    app.run(debug=True)
