from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modèle pour les produits (test)
class Produit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    prix = db.Column(db.Float, nullable=False)
    stock = db.Column(db.Integer, nullable=False)

@app.route('/')
def index():
    produits = Produit.query.all()
    if produits is None:
        produits = []
    return render_template('home.html', produits=produits)


@app.route('/admin')
def admin():
    produits = Produit.query.all()
    return render_template('admin.html', produits=produits)

@app.route('/ajouter', methods=['POST'])
def ajouter_produit():
    if request.method == 'POST':
        nom = request.form['nom']
        description = request.form['description']
        prix = float(request.form['prix'])
        stock = int(request.form['stock'])

        nouveau_produit = Produit(nom=nom, description=description, prix=prix, stock=stock)
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
    #produit = db.session.get(Produit, id)
    produit = Produit.query.get(id)
    produits = Produit.query.all()
    if not produits:  # Si aucun produit trouvé
        produits = []  # Passez une liste vide
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
    try:
        db.session.commit()
        return redirect(url_for('admin')), 200
    except Exception as e:
        db.session.rollback()
        return f"Erreur lors de la modification : {e}", 500



if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Créer la base de données si elle n'existe pas
    app.run(debug=True)
