"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from models import db, User, Favoritos, Personajes, Planetas
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
                    "msg": "User no encontrado"
                }), 404


    ##########################
    ## METODO POST DE /user ##
    ##########################
    if request.method == 'POST':
        body = request.json

        if not body.get("email"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        if not body.get("password"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
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

        if not body.get("email"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        if not body.get("password"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        user_update = User.query.filter_by(id = user_id).first()

        if user_update is None:
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
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
                "msg": "User no encontrado, intenta de nuevo"
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
@app.route('/personajes', methods=['GET', 'POST'])
@app.route('/personajes/<int:personaje_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_personajes(personaje_id = None):

    ################################################
    ## METODO GET DE /personajes y /personajes/id ##
    ################################################
    if request.method == 'GET':
        if personaje_id is None:

            personajes = Personajes.query.all()
            personajes = list(map(
                lambda personaje: personaje.serialize(),
                personajes
            ))
            return jsonify(personajes), 200
        else:
            personaje = Personajes.query.filter_by(id = personaje_id).first()
            if personaje is not None:
                return jsonify(personaje.serialize()), 200
            else:
                return jsonify({
                    "msg": "Personaje no encontrado"
                }), 404


    ################################
    ## METODO POST DE /personajes ##
    ################################
    if request.method == 'POST':
        body = request.json

        if not body.get("nombre"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        
        if not body.get("edad"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        personaje = Personajes(nombre=body["nombre"], genero=body["genero"], edad=body["edad"])
        try:
            db.session.add(personaje)
            db.session.commit()
            return jsonify(personaje.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500

    ################################
    # METODO PUT DE /personajes/id #
    ################################
    if request.method == 'PUT':
        body = request.json

        if not body.get("nombre"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        
        if not body.get("edad"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        personaje_update = Personajes.query.filter_by(id = personaje_id).first()

        if personaje_update is None:
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        try:
            personaje_update.nombre = body["nombre"]
            personaje_update.genero = body["genero"]
            personaje_update.edad = body["edad"]
            db.session.commit()
            return jsonify(personaje_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


    #####################################
    ## METODO DELETE DE /personajes/id ##
    #####################################
    if request.method == 'DELETE':
        
        personaje_delete = Personajes.query.filter_by(id = personaje_id).first()

        if personaje_delete is None:
            return jsonify({
                "msg": "Personaje no encontrado, intenta de nuevo"
            }), 404
        
        db.session.delete(personaje_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)
    

#######################
## Rutas de planetas ##
#######################
@app.route('/planetas', methods=['GET', 'POST'])
@app.route('/planetas/<int:planeta_id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_planetas(planeta_id = None):

    ############################################
    ## METODO GET DE /planetas y /planetas/id ##
    ############################################
    if request.method == 'GET':
        if planeta_id is None:

            planetas = Planetas.query.all()
            planetas = list(map(
                lambda planeta : planeta.serialize(),
                planetas
            ))
            return jsonify(planetas), 200
        else:
            planeta = Planetas.query.filter_by(id = planeta_id).first()
            if planeta_id is not None:
                return jsonify(planeta.serialize()), 200
            else:
                return jsonify({
                    "msg": "Planeta no encontrado"
                }), 404

    ##############################
    ## METODO POST DE /planetas ##
    ##############################
    if request.method == 'POST':
        body = request.json

        if not body.get("nombre"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        if not body.get("clima"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        
        if not body.get("terreno"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        
        if not body.get("poblacion"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        planeta = Planetas(nombre=body["nombre"], clima=body["clima"], terreno=body["terreno"], poblacion=body["poblacion"])
        try:
            db.session.add(planeta)
            db.session.commit()
            return jsonify(planeta.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500

    ##############################
    # METODO PUT DE /planetas/id #
    ##############################
    if request.method == 'PUT':
        body = request.json

        if not body.get("nombre"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        if not body.get("clima"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        
        if not body.get("terreno"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        
        if not body.get("poblacion"):
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400

        planeta_update = Planetas.query.filter_by(id = planeta_id).first()

        if planeta_update is None:
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        try:
            planeta_update.nombre = body["nombre"]
            planeta_update.clima = body["clima"]
            planeta_update.terreno = body["terreno"]
            planeta_update.poblacion = body["poblacion"]
            db.session.commit()
            return jsonify(planeta_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


    ###################################
    ## METODO DELETE DE /planetas/id ##
    ###################################
    if request.method == 'DELETE':
        
        planeta_delete = Planetas.query.filter_by(id = planeta_id).first()

        if planeta_delete is None:
            return jsonify({
                "msg": "Personaje no encontrado, intenta de nuevo"
            }), 404
        
        db.session.delete(planeta_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)


##################################
##### Favoritos de cada User #####
##################################
@app.route('/user/favoritos', methods = ['GET'])
@jwt_required()
def handle_get_favoritos():

    user_id = get_jwt_identity()
    favoritos = Favoritos.query.filter_by( user_id = user_id ).all()

    favoritos_serialize = [favorito.serialize() for favorito in favoritos]

    # la linea 401 es la manera resumida de hacer esto:
    # favoritos_serialize = []
    # for favorito in favoritos:
    #     favoritos_serialize.append(favorito.serialize())
  
    return jsonify(favoritos_serialize)

###############################
# Planetas favoritos del User #
###############################
@app.route('/user/favoritos/planetas', methods = ['GET', 'POST'])
@app.route('/user/favoritos/planetas/<int:planeta_id>', methods = ['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_planetas_favoritos( planeta_id = None ):

    #######################################
    # Identity reutilizable en la funcion #
    #######################################
    user_id = get_jwt_identity()

    #################################################
    # METODO GET DE LOS PLANETAS FAVORITOS POR USER #
    #################################################
    if request.method == 'GET':

        if planeta_id is None:
            favoritos = Favoritos.query.filter_by( user_id = user_id ).all()
            planetas_favoritos = []
            
            for favorito in favoritos:
                if favorito.planeta_id is not None:
                    planetas_favoritos.append(favorito.serialize())

            if not planetas_favoritos:
                return jsonify({
                    "msg": "No tiene Planetas favoritos"
                }), 404
            else:
                return jsonify(planetas_favoritos), 200

        if planeta_id is not None:

            planeta = Favoritos.query.filter_by(user_id = user_id, planeta_id = planeta_id).first()

            if planeta is not None:
                return jsonify(planeta.serialize()), 200
            else:
                return jsonify({
                    "msg": "Planeta no encontrado"
                }), 404

    ##################################################
    # METODO POST DE LOS PLANETAS FAVORITOS POR USER #
    ##################################################
    if request.method == 'POST':
        body = request.json

        planeta = Favoritos(planeta_id=body["planeta_id"], user_id=user_id)
        try:
            db.session.add(planeta)
            db.session.commit()
            return jsonify(planeta.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500

    #################################################
    # METODO PUT DE LOS PLANETAS FAVORITOS POR USER #
    #################################################
    if request.method == 'PUT':
        body = request.json

        planeta_update = Favoritos.query.filter_by(planeta_id = planeta_id, user_id=user_id).first()

        if planeta_update is None:
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        try:
            planeta_update.personaje_id = body["personaje_id"]
            planeta_update.planeta_id = body["planeta_id"]
            db.session.commit()
            return jsonify(planeta_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)

    ####################################################
    # METODO DELETE DE LOS PLANETAS FAVORITOS POR USER #
    ####################################################
    if request.method == 'DELETE':
        
        planeta_delete = Favoritos.query.filter_by(user_id = user_id, planeta_id = planeta_id).first()

        if planeta_delete is None:
            return jsonify({
                "msg": "Personaje no encontrado, intenta de nuevo"
            }), 404
        
        db.session.delete(planeta_delete)

        try:
            db.session.commit()
            return jsonify([]), 204
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)

#################################
# Personajes favoritos del User #
#################################
@app.route('/user/favoritos/personajes', methods = ['GET', 'POST'])
@app.route('/user/favoritos/personajes/<int:personaje_id>', methods = ['GET', 'PUT', 'DELETE'])
@jwt_required()
def handle_personajes_favoritos( personaje_id = None):

    #######################################
    # Identity reutilizable en la funcion #
    #######################################
    user_id = get_jwt_identity()

    ###################################################
    # METODO GET DE LOS PERSONAJES FAVORITOS POR USER #
    ###################################################
    if request.method == 'GET':
        if personaje_id is None:
            favoritos = Favoritos.query.filter_by( user_id = user_id ).all()

            personajes_favoritos = []

            for favorito in favoritos:
                if favorito.personaje_id is not None:
                    personajes_favoritos.append(favorito.serialize())

            if not personajes_favoritos:
                return jsonify({
                    "msg": "No tiene Personajes favoritos"
                }), 404
            else:
                return jsonify(personajes_favoritos), 200

        if personaje_id is not None:

            personaje = Favoritos.query.filter_by(user_id = user_id, personaje_id = personaje_id).first()

            if personaje is not None:
                return jsonify(personaje.serialize()), 200
            else:
                return jsonify({
                    "msg": "Personaje no encontrado"
                }), 404
    

    ####################################################
    # METODO POST DE LOS PERSONAJES FAVORITOS POR USER #
    ####################################################
    if request.method == 'POST':
        body = request.json

        personaje = Favoritos(personaje_id=body["personaje_id"], user_id=user_id)
        try:
            db.session.add(personaje)
            db.session.commit()
            return jsonify(personaje.serialize()), 201

        except Exception as error:
            db.session.rollback()
            return jsonify(error.args), 500


    ###################################################
    # METODO PUT DE LOS PERSONAJES FAVORITOS POR USER #
    ###################################################
    if request.method == 'PUT':
        body = request.json

        personaje_update = Favoritos.query.filter_by(personaje_id = personaje_id, user_id=user_id).first()

        if personaje_update is None:
            return jsonify({
                "msg": "Algo está mal, intenta de nuevo"
            }), 400
        try:
            personaje_update.personaje_id = body["personaje_id"]
            db.session.commit()
            return jsonify(personaje_update.serialize()), 202
        except Exception as error:
            db.session.rollback()
            return jsonify(error.args)

    ######################################################
    # METODO DELETE DE LOS PERSONAJES FAVORITOS POR USER #
    ######################################################
    if request.method == 'DELETE':
        
        personaje_delete = Favoritos.query.filter_by(user_id = user_id, personaje_id = personaje_id).first()

        if personaje_delete is None:
            return jsonify({
                "msg": "Personaje no encontrado, intenta de nuevo"
            }), 404
        
        db.session.delete(personaje_delete)

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
            "msg": "No se ha encontrado el usuario"
        }), 404
        print(user)        
    else:
        return jsonify({
            "msg": "Algo está mal, intenta de nuevo"
        }), 400






# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
