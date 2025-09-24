#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/")
def index():
    return "<h1>Code challenge</h1>"

class Restaurants(Resource):
    def get(self):
        restaurants = [r.to_dict() for r in Restaurant.query.all()] ## getting all rows 
        return make_response(restaurants, 200)


class RestaurantID(Resource):
    def get(self, id):
        restaurant = Restaurant.query.get(id)
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        data = restaurant.to_dict()
        data["restaurant_pizzas"] = [
            {
                "id": rp.id,
                "price": rp.price,
                "pizza_id": rp.pizza_id,
                "restaurant_id": rp.restaurant_id,
                "pizza": rp.pizza.to_dict()
            }
            for rp in restaurant.restaurant_pizzas
        ]
        return make_response(data, 200)

    def delete(self, id):
        restaurant = Restaurant.query.get(id) ## get the restaurant by id 
        if not restaurant:
            return make_response({"error": "Restaurant not found"}, 404)

        db.session.delete(restaurant)
        db.session.commit()
        return make_response({}, 204)


class Pizzas(Resource):
    def get(self):
        pizzas = [p.to_dict() for p in Pizza.query.all()]
        return make_response(pizzas, 200)


class RestaurantPizzas(Resource):
    def post(self):
        data = request.get_json()
        try:
            new_rp = RestaurantPizza(
                price=data["price"],
                pizza_id=data["pizza_id"],
                restaurant_id=data["restaurant_id"]
            )
            db.session.add(new_rp)
            db.session.commit()

            response = new_rp.to_dict()
            response["pizza"] = new_rp.pizza.to_dict()
            response["restaurant"] = new_rp.restaurant.to_dict()

            return make_response(response, 201)
        except Exception as e:
            return make_response({"errors": ["validation errors"]}, 400)



api.add_resource(Restaurants, "/restaurants")
api.add_resource(RestaurantID, "/restaurants/<int:id>")
api.add_resource(Pizzas, "/pizzas")
api.add_resource(RestaurantPizzas, "/restaurant_pizzas")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
