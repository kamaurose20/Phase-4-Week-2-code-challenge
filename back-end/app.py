#!/usr/bin/env python3

from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from models import db
from flask_migrate import Migrate

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///server.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Importing models after initializing db
from models import Restaurant, Pizza, RestaurantPizza

# Routes

@app.route('/')
def home():
    return ''


@app.route('/restaurants', methods=['GET'])
def get_restaurants():
    restaurants = Restaurant.query.all()
    data = [{"id": restaurant.id, "name": restaurant.name, "address": restaurant.address} for restaurant in restaurants]
    return jsonify(data)


@app.route('/restaurants/<int:restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if restaurant:
        data = {
            "id": restaurant.id,
            "name": restaurant.name,
            "address": restaurant.address,
            "pizzas": [
                {"id": rp.pizza.id, "name": rp.pizza.name, "ingredients": rp.pizza.ingredients, "price": rp.price}
                for rp in restaurant.restaurant_pizzas
            ]
        }
        return jsonify(data)
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route('/restaurants/<int:restaurant_id>', methods=['DELETE'])
def delete_restaurant(restaurant_id):
    restaurant = Restaurant.query.get(restaurant_id)
    if restaurant:
        RestaurantPizza.query.filter_by(restaurant_id=restaurant.id).delete()
        db.session.delete(restaurant)
        db.session.commit()
        return jsonify({}), 204
    else:
        return jsonify({"error": "Restaurant not found"}), 404


@app.route('/pizzas', methods=['GET'])
def get_pizzas():
    pizzas = Pizza.query.all()
    data = [{"id": pizza.id, "name": pizza.name, "ingredients": pizza.ingredients} for pizza in pizzas]
    return jsonify(data)


@app.route('/restaurant_pizzas', methods=['POST'])
def create_restaurant_pizza():
    data = request.get_json()
    price = data.get("price")
    pizza_id = data.get("pizza_id")
    restaurant_id = data.get("restaurant_id")

    if not (price and pizza_id and restaurant_id):
        return jsonify({"errors": ["Missing required fields"]}), 400

    pizza = Pizza.query.get(pizza_id)
    restaurant = Restaurant.query.get(restaurant_id)
    if not (pizza and restaurant):
        return jsonify({"errors": ["Pizza or Restaurant not found"]}), 404

    restaurant_pizza = RestaurantPizza(price=price, pizza=pizza, restaurant=restaurant)
    db.session.add(restaurant_pizza)
    db.session.commit()

    return jsonify({
        "id": pizza.id,
        "name": pizza.name,
        "ingredients": pizza.ingredients
    }), 201

if __name__ == '__main__':
    app.run(port=5555)
