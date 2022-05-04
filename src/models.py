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
    name = db.Column(db.String(60), nullable=False)
    nature = db.Column(db.String(50), nullable=False)
    nature_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (db.UniqueConstraint(
    'user_id',
    'name',
    name="dont_repeat_favorites"
    ),)

    def __repr__(self):
        return f"<Favorites object {self.id}>"

    def serialize(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "nature": self.nature,
            "nature_id": self.nature_id
        }


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), nullable=False)
    height = db.Column(db.Integer, nullable=False)
    mass = db.Column(db.Integer, nullable=False)
    hair_color = db.Column(db.String(50), nullable=False)
    skin_color = db.Column(db.String(50), nullable=False)
    eye_color = db.Column(db.String(50), nullable=False)
    birth_year = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(50), nullable=False)


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

    def __init__(self, *args, **kwargs):

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore the other values: {error.args}")

    @classmethod
    def create(cls, data):
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("Something failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)


class Planets(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(50), unique=True, nullable=False)
    diameter = db.Column(db.Float, nullable=False)
    climate = db.Column(db.String(50), nullable=False)
    gravity = db.Column(db.String(50), nullable=False)
    terrain = db.Column(db.String(50), nullable=False)
    surface_water = db.Column(db.String(50), nullable=False)
    population = db.Column(db.String(100))
    __table_args__ = (db.UniqueConstraint(
    'diameter',
    'name',
    name="dont_repeat_planets"
    ),)

    
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

    def __init__(self, *args, **kwargs):

        for (key, value) in kwargs.items():
            if hasattr(self, key):
                attr_type = getattr(self.__class__, key).type

                try:
                    attr_type.python_type(value)
                    setattr(self, key, value)
                except Exception as error:
                    print(f"ignore the other values: {error.args}")

    @classmethod
    def create(cls, data):
        instance = cls(**data)
        if (not isinstance(instance, cls)):
            print("Something failed")
            return None
        db.session.add(instance)
        try:
            db.session.commit()
            print(f"Created: {instance.name}")
            return instance
        except Exception as error:
            db.session.rollback()
            print(error.args)