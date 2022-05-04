from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)

    favorites = db.relationship('Favorites', backref='user', uselist=True)

    def __repr__(self):
        return f"<User: {self.email}>"

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }


class Favorites(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    planet_id = db.Column(db.Integer, db.ForeignKey('planets.id'))
    people_id = db.Column(db.Integer, db.ForeignKey('people.id'))
    

    def __repr__(self):
        return f"<Favorites object {self.id}>"

    def serialize(self):
        return {
            "planet_id": self.planet_id,
            'people_id': self.people_id
        }


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(30), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=False)
    hair_color = db.Column(db.String(20), nullable=False)
    skin_color = db.Column(db.String(20), nullable=False)
    eye_color = db.Column(db.String(20), nullable=False)
    birth_year = db.Column(db.String(30), nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    favorites = db.relationship('Favorites', backref='people', uselist=True)


    def __repr__(self):
        return f"<People id: {self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender
        }


class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(40), unique=True, nullable=False)
    diameter = db.Column(db.Integer, nullable=False)
    climate = db.Column(db.String(20), nullable=False)
    gravity = db.Column(db.String(30), nullable=False)
    terrain = db.Column(db.String(20), nullable=False)
    surface_water = db.Column(db.Integer, nullable=False)
    population = db.Column(db.Float, nullable=False)
    favorites = db.relationship('Favorites', backref='planets', uselist=True)

    
    def __repr__(self):
        return f"<Planet id: {self.id}>"

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "diameter": self.diameter,
            "climate": self.climate,
            "gravity": self.gravity,
            "terrain": self.terrain,
            "surface_water": self.surface_water,
            "population": self.population
        }