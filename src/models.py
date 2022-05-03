from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    favoritos = db.relationship('Favoritos', backref='user', uselist=True)

    def __repr__(self):
        return f"User: {self.email}"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Favoritos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    personaje_id = db.Column(db.Integer, db.ForeignKey('personajes.id'), nullable=True)
    planeta_id = db.Column(db.Integer, db.ForeignKey('planetas.id'), nullable=True)


    def __repr__(self):
        return f"<Favoritos object {self.id}>"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "personaje_id": self.personaje_id,
            "planeta_id": self.planeta_id
        }


class Personajes(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(30), unique=True, nullable=False)
    genero = db.Column(db.String(20), nullable=False)
    edad = db.Column(db.Float, nullable=False)
    favorito = db.relationship('Favoritos', backref='personajes', uselist=True)


    def __repr__(self):
        return f"Id de Personaje: {self.id} "

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "genero": self.genero,
            "edad": self.edad
        }


class Planetas(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    nombre = db.Column(db.String(40), unique=True, nullable=False)
    clima = db.Column(db.String(20), nullable=False)
    terreno = db.Column(db.String(20), nullable=False)
    poblacion = db.Column(db.Float, nullable=False)
    favorito = db.relationship('Favoritos', backref='planetas', uselist=True)
    
    
    def __repr__(self):
        return f"Id de Planeta: {self.id}"

    def serialize(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "clima": self.clima,
            "terreno": self.terreno,
            "poblacion": self.poblacion
        }