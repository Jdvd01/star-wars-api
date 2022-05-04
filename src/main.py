"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
import requests
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Favorites, People, Planets
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('FLASK_APP_KEY')
jwt = JWTManager(app)
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

####################
# URL reutilizable #
####################
URL_BASE = "https://swapi.dev/api"

@app.route('/population/planets', methods = ['POST'])
def handle_population_planets():
    response = requests.get(f'{URL_BASE}/planets/?page=1&limit=20')
    response = response.json()
    result_planets = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        result_planets.append(detail)

    instances = []

    for planet in result_planets:
        instance = Planets.create(planet)
        instances.append(instance)

    return jsonify(list(map( lambda inst: inst.serialize(), instances))), 200

@app.route('/population/people', methods = ['POST'])
def handle_population_people():
    response = requests.get(f'{URL_BASE}/people/?page=1&limit=20')
    response = response.json()
    result_people = []

    for result in response['results']:
        detail = requests.get(result['url'])
        detail = detail.json()
        result_people.append(detail)

    instances = []

    for character in result_people:
        instance = People.create(character)
        instances.append(instance)

    return jsonify(list(map( lambda inst: inst.serialize(), instances))), 200


###################
## Rutas de user ##
###################
@app.route('/user', methods=['GET', 'POST'])
@app.route('/user/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_user(user_id = None):
    
    ####################################
    ## METODO GET DE /user y /user/id ##
    ####################################
    if request.method == 'GET':

        if user_id is None:
            
            users = User.query.all()
            users = list(map(
                lambda user : user.serialize(),
                users
            ))
            return jsonify(users), 200
        else:
            user = User.query.filter_by(id = user_id).first()
            if user is not None:
                return jsonify(user.serialize()), 200
            else:
                return jsonify({
                    "msg": "User not found"
                }), 404


    ##########################
    ## METODO POST DE /user ##
    ##########################
    if request.method == 'POST':
        body = request.json

        if not body.get("email") or not body.get("password"):
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400

        user = User(email=body["email"], password=body["password"])
        try:
            db.session.add(user)
            db.session.commit()
            return jsonify(user.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500
    

    ##########################
    # METODO PUT DE /user/id #
    ##########################
    if request.method == 'PUT':
        body = request.json

        if not body.get("email") or not body.get("password"):
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400

        user_update = User.query.filter_by(id = user_id).first()

        if user_update is None:
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400
        try:
            user_update.email = body["email"]
            user_update.password = body["password"]
            db.session.commit()
            return jsonify(user_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


    ###############################
    ## METODO DELETE DE /user/id ##
    ###############################
    if request.method == 'DELETE':
        
        user_delete = User.query.filter_by(id = user_id).first()

        if user_delete is None:
            return jsonify({
                "msg": "User not found, try again"
            }), 404
        
        db.session.delete(user_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


#########################
## Rutas de personajes ##
#########################
@app.route('/people', methods=['GET', 'POST'])
@app.route('/people/<int:character_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_people(character_id = None):

    ########################################
    ## METODO GET DE /people y /people/id ##
    ########################################
    if request.method == 'GET':
        if character_id is None:

            character = People.query.all()
            character = list(map(
                lambda character: character.serialize(),
                character
            ))
            return jsonify(character), 200
        else:
            character = People.query.filter_by(id = character_id).first()
            if character is not None:
                return jsonify(character.serialize()), 200
            else:
                return jsonify({
                    "msg": "Character not found"
                }), 404


    ############################
    ## METODO POST DE /people ##
    ############################
    if request.method == 'POST':
        body = request.json

        if not body.get("name") or not body.get("height") or not body.get("mass") or not body.get("hair_color") or not body.get("skin_color") or not body.get("eye_color") or not body.get("birth_year") or not body.get("gender"):
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400

        character = People(
            name=body["name"],
            height=body["height"], 
            mass=body["mass"],
            hair_color=body["hair_color"],
            skin_color=body["skin_color"], 
            eye_color=body["eye_color"],
            birth_year=body["birth_year"],
            gender=body["gender"]
            )
        try:
            db.session.add(character)
            db.session.commit()
            return jsonify(character.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500

    ############################
    # METODO PUT DE /people/id #
    ############################
    if request.method == 'PUT':
        body = request.json

        if not body.get("name") or not body.get("height") or not body.get("mass") or not body.get("hair_color") or not body.get("skin_color") or not body.get("eye_color") or not body.get("birth_year") or not body.get("gender"):
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400

        character_update = People.query.filter_by(id = character_id).first()

        if character_update is None:
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400
        try:
            character_update.name = body.get("name")
            character_update.height = body.get("height")
            character_update.mass = body.get("mass")
            character_update.hair_color = body.get("hair_color")
            character_update.skin_color = body.get("skin_color")
            character_update.eye_color = body.get("eye_color")
            character_update.birth_year = body.get("birth_year")
            character_update.gender = body.get("gender")
            db.session.commit()
            return jsonify(character_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


    #################################
    ## METODO DELETE DE /people/id ##
    #################################
    if request.method == 'DELETE':
        
        character_delete = People.query.filter_by(id = character_id).first()

        if character_delete is None:
            return jsonify({
                "msg": "Character not found, try again"
            }), 404
        
        db.session.delete(character_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)
    

#######################
## Rutas de planetas ##
#######################
@app.route('/planets', methods=['GET', 'POST'])
@app.route('/planets/<int:planet_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_planetas(planet_id = None):

    ##########################################
    ## METODO GET DE /planets y /planets/id ##
    ##########################################
    if request.method == 'GET':
        if planet_id is None:

            planets = Planets.query.all()
            planets = list(map(
                lambda planet : planet.serialize(),
                planets
            ))
            return jsonify(planets), 200
        else:
            planet = Planets.query.filter_by(id = planet_id).first()
            if planet_id is not None:
                return jsonify(planet.serialize()), 200
            else:
                return jsonify({
                    "msg": "Planet not found"
                }), 404

    #############################
    ## METODO POST DE /planets ##
    #############################
    if request.method == 'POST':
        body = request.json

        if not body.get("name") or not body.get("diameter") or not body.get("climate") or not body.get("gravity") or not body.get("terrain") or not body.get("surface_water") or not body.get("population"):
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400

        planet = Planets(
            name=body["name"],
            diameter=body["diameter"], 
            climate=body["climate"],
            gravity=body["gravity"],
            terrain=body["terrain"], 
            surface_water=body["surface_water"],
            population=body["population"]
            )
        try:
            db.session.add(planet)
            db.session.commit()
            return jsonify(planet.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500

    #############################
    # METODO PUT DE /planets/id #
    #############################
    if request.method == 'PUT':
        body = request.json

        if not body.get("name") or not body.get("diameter") or not body.get("climate") or not body.get("gravity") or not body.get("terrain") or not body.get("surface_water") or not body.get("population"):
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400

        planet_update = Planets.query.filter_by(id = planet_id).first()

        if planet_update is None:
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400
        try:
            planet_update.name = body["name"]
            planet_update.diameter = body["diameter"]
            planet_update.climate = body["climate"]
            planet_update.gravity = body["gravity"]
            planet_update.terrain = body["terrain"]
            planet_update.surface_water = body["surface_water"]
            planet_update.population = body["population"]
            db.session.commit()
            return jsonify(planet_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


    ##################################
    ## METODO DELETE DE /planets/id ##
    ##################################
    if request.method == 'DELETE':
        
        planet_delete = Planets.query.filter_by(id = planet_id).first()

        if planet_delete is None:
            return jsonify({
                "msg": "Character not found, try again"
            }), 404
        
        db.session.delete(planet_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


##################################
##### Favoritos de cada User #####
##################################
@app.route('/user/favorites', methods = ['GET'])
@jwt_required()
def handle_get_favorites():

    #########################
    # Identity reutilizable #
    #########################
    user_id = get_jwt_identity()
    
    favorites = Favorites.query.filter_by( user_id = user_id ).all()

    favorites_serialize = [favorito.serialize() for favorito in favorites]

    # la linea 401 es la manera resumida de hacer esto:
    # favorites_serialize = []
    # for favorite in favorites:
    #     favorites_serialize.append(favorite.serialize())
  
    return jsonify(favorites_serialize)

###############################
# Planetas favoritos del User #
###############################
@app.route('/user/favorites/planets', methods = ['GET', 'POST'])
@app.route('/user/favorites/planets/<int:planet_id>', methods = ['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_planets_favorites( planet_id = None ):

    #########################
    # Identity reutilizable #
    #########################
    user_id = get_jwt_identity()

    #################################################
    # METODO GET DE LOS PLANETAS FAVORITOS POR USER #
    #################################################
    if request.method == 'GET':

        if planet_id is None:
            favorites = Favorites.query.filter_by( user_id = user_id ).all()
            favorite_planets = []
            
            for favorite in favorites:
                if favorite.nature_id is not None and favorite.nature == 'Planet':
                    favorite_planets.append(favorite.serialize())

            if not favorite_planets:
                return jsonify({
                    "msg": "U dont have favorite planets"
                }), 404
            else:
                return jsonify(favorite_planets), 200

        if planet_id is not None:

            planet = Favorites.query.filter_by(user_id = user_id, nature_id = planet_id, nature='Planet').first()

            if planet is not None:
                return jsonify(planet.serialize()), 200
            else:
                return jsonify({
                    "msg": "Planet not found"
                }), 404

    ##################################################
    # METODO POST DE LOS PLANETAS FAVORITOS POR USER #
    ##################################################
    if request.method == 'POST':
        body = request.json

        planet = Favorites(
            name=body["name"],
            nature = "Planet",
            nature_id = body["nature_id"],
            user_id=user_id
            )
        try:
            db.session.add(planet)
            db.session.commit()
            return jsonify(planet.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500

    #################################################
    # METODO PUT DE LOS PLANETAS FAVORITOS POR USER #
    #################################################
    if request.method == 'PUT':
        body = request.json

        planet_update = Favorites.query.filter_by(nature_id = planet_id, user_id=user_id, nature='Planet').first()

        if planet_update is None:
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400
        try:
            planet_update.name = body["name"]
            db.session.commit()
            return jsonify(planet_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)

    ####################################################
    # METODO DELETE DE LOS PLANETAS FAVORITOS POR USER #
    ####################################################
    if request.method == 'DELETE':
        
        planet_delete = Favorites.query.filter_by(user_id = user_id, nature_id = planet_id, nature='Planet').first()

        if planet_delete is None:
            return jsonify({
                "msg": "Character not found, try again"
            }), 404
        
        db.session.delete(planet_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)

#################################
# Personajes favoritos del User #
#################################
@app.route('/user/favorites/people', methods = ['GET', 'POST'])
@app.route('/user/favorites/people/<int:character_id>', methods = ['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_personajes_favoritos( character_id = None):


    #######################################
    # Identity reutilizable en la funcion #
    #######################################
    user_id = get_jwt_identity()

    ###################################################
    # METODO GET DE LOS PERSONAJES FAVORITOS POR USER #
    ###################################################
    if request.method == 'GET':
        if character_id is None:
            favorites = Favorites.query.filter_by( user_id = user_id ).all()

            favorite_characters = []

            for favorite in favorites:
                if favorite.nature_id is not None and favorite.nature == 'People':
                    favorite_characters.append(favorite.serialize())

            if not favorite_characters:
                return jsonify({
                    "msg": "U dont have favorites characters"
                }), 404
            else:
                return jsonify(favorite_characters), 200

        if character_id is not None:

            character = Favorites.query.filter_by(user_id = user_id, nature_id = character_id, nature='People').first()

            if character is not None:
                return jsonify(character.serialize()), 200
            else:
                return jsonify({
                    "msg": "Character not found"
                }), 404
    

    ####################################################
    # METODO POST DE LOS PERSONAJES FAVORITOS POR USER #
    ####################################################
    if request.method == 'POST':
        body = request.json

        character = Favorites(
            name = body["name"],
            nature = 'People',
            nature_id = body["nature_id"],
            user_id=user_id
            )
        try:
            db.session.add(character)
            db.session.commit()
            return jsonify(character.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500


    ###################################################
    # METODO PUT DE LOS PERSONAJES FAVORITOS POR USER #
    ###################################################
    if request.method == 'PUT':
        body = request.json

        character_update = Favorites.query.filter_by(nature_id = character_id, user_id=user_id, nature='People').first()

        if character_update is None:
            return jsonify({
                "msg": "Something is wrong, try again"
            }), 400
        try:
            character_update.name = body["name"]
            db.session.commit()
            return jsonify(character_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)

    ######################################################
    # METODO DELETE DE LOS PERSONAJES FAVORITOS POR USER #
    ######################################################
    if request.method == 'DELETE':
        
        character_delete = Favorites.query.filter_by(user_id = user_id, nature_id = character_id, nature='People').first()

        if character_delete is None:
            return jsonify({
                "msg": "Character not found"
            }), 404
        
        db.session.delete(character_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


#############
### login ###
#############
@app.route('/login', methods = ['POST'])
def handle_login():

    email = request.json.get("email", None)
    password = request.json.get("password", None)

    if email is not None and password is not None:
        user = User.query.filter_by(email=email, password=password).one_or_none()

        if user is not None:
            create_token = create_access_token(identity = user.id)
            return jsonify({
                "email": user.email,
                "token": create_token,
                "user_id": user.id,
            })
        else:
            return jsonify({
            "msg": "User not found"
        }), 404
        print(user)        
    else:
        return jsonify({
            "msg": "Something is wrong, try again"
        }), 400

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)