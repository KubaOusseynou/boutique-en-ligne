import os
from functools import wraps
from flask import Flask, render_template, request, session, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Configurer l'application Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'f2420273c4ed2f2776f04f838472438486463ffcd998a778'
app.config['UPLOAD_FOLDER'] = 'static/images'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16 Mo

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Modèle pour les utilisateurs
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    prenom = db.Column(db.String(100), nullable=True)
    nom = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(200), nullable=False)
    admin = db.Column(db.Boolean, default=False, nullable=True)

# Modèle pour les produits
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    prix = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(255), nullable=True)

# Vérification des fichiers autorisés
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Décorateur pour exiger une connexion
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'utilisateur_id' not in session:
            flash("Vous devez être connecté pour accéder à cette page.", "danger")
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Route principale
@app.route('/')
def index():
    produits = Produit.query.all()
    return render_template('home.html', produits=produits)

# Route pour la page d'administration
@app.route('/admin')
@login_required
def admin():
    produits = Produit.query.all()
    return render_template('admin.html', produits=produits)

# Route pour la connexion
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        #nom = request.form['nom']
        #prenom = request.form['prenom']
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

        utilisateur = Utilisateur.query.filter_by(email=email).first()
        if utilisateur and check_password_hash(utilisateur.mot_de_passe, mot_de_passe):
            session['utilisateur_id'] = utilisateur.id
            session['email'] = utilisateur.email
            session['prenom'] = utilisateur.prenom
            session['nom'] = utilisateur.nom
            session['admin'] = utilisateur.admin
            flash("Connexion réussie.", "success")
            return redirect(url_for('index'))
        else:
            flash("Identifiants invalides.", "danger")

    return render_template('login.html')

# Route pour la déconnexion
@app.route('/logout')
def logout():
    session.clear()
    flash("Déconnexion réussie.", "success")
    return redirect(url_for('login'))

# Route pour l'inscription
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form['nom']
        prenom = request.form['prenom']
        email = request.form['email']
        mot_de_passe = request.form['mot_de_passe']

        if Utilisateur.query.filter_by(email=email).first():
            flash("Cet email est déjà utilisé.", "danger")
            return redirect(url_for('register'))

        mot_de_passe_hache = generate_password_hash(mot_de_passe, method='pbkdf2:sha256')
        nouvel_utilisateur = Utilisateur(email=email,            nom=nom,
            prenom=prenom, mot_de_passe=mot_de_passe_hache)
        db.session.add(nouvel_utilisateur)
        db.session.commit()
        flash("Inscription réussie. Veuillez vous connecter.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Route pour ajouter un produit
@app.route('/ajouter', methods=['POST'])
@login_required
def ajouter_produit():
    nom = request.form['nom']
    description = request.form['description']
    prix = float(request.form['prix'])
    stock = int(request.form['stock'])
    image = request.files.get('image')
    image_url = None

    if image and allowed_file(image.filename):
        filename = secure_filename(image.filename)
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image.save(image_path)
        image_url = f'/static/images/{filename}'

    produit = Produit(nom=nom, description=description, prix=prix, stock=stock, image_url=image_url)
    db.session.add(produit)
    db.session.commit()
    return redirect(url_for('admin'))

# Route pour supprimer un produit
@app.route('/supprimer/<int:id>')
@login_required
def supprimer_produit(id):
    produit = Produit.query.get_or_404(id)
    db.session.delete(produit)
    db.session.commit()
    return redirect(url_for('admin'))

# Route pour modifier un produit
@app.route('/modifier/<int:id>', methods=['GET', 'POST'])
@login_required
def modifier_produit(id):
    produit = Produit.query.get_or_404(id)
    if request.method == 'POST':
        produit.nom = request.form['nom']
        produit.description = request.form['description']
        produit.prix = float(request.form['prix'])
        produit.stock = int(request.form['stock'])

        if 'image' in request.files:
            image = request.files['image']
            if image.filename:
                filename = secure_filename(image.filename)
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                image.save(image_path)
                produit.image_url = f'/static/images/{filename}'
        try:
            db.session.commit()
            return redirect(url_for('admin'))
        except Exception as e:
            db.session.rollback()
            return f"Erreur lors de la modification : {e}", 500

        # Méthode GET : afficher la page de modification
    produits = Produit.query.all()
    return render_template('admin.html', produits=produits, produit_modifie=produit)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
