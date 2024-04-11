from flask import (
    Flask,
    jsonify,
    request,
)  # handling the import, giving us access to Flask and its functionality
from flask_marshmallow import Marshmallow
from marshmallow import fields, ValidationError

# local import for db connection
from connect_db import connect_db, Error

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False
ma = Marshmallow(app)


class memberSchema(ma.Schema):
    id = fields.Int(dumponly=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("id", "name", "email", "phone")


member_schema = memberSchema()
members_schema = memberSchema(many=True)


@app.route("/members", methods=["GET"])
def get_members():
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members"
        cursor.execute(query)
        member = cursor.fetchall()

        return members_schema.jsonify(member)

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members/<int:id>", methods=["GET"])
def get_member(id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = "SELECT * FROM Members WHERE id = %s"
        cursor.execute(query, (id,))
        member = cursor.fetchall()

        return members_schema.jsonify(member)

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members", methods=["POST"])
def add_member():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        query = "INSERT INTO members (name, email, phone) VALUES (%s,%s,%s)"
        cursor.execute(
            query, (member_data["name"], member_data["email"], member_data["phone"])
        )
        conn.commit()
        return jsonify({"message": "Order was successfully added"}), 201

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members/<int:id>", methods=["PUT"])
def update_member(id):
    try:
        # Validate incoming data
        member_data = member_schema.load(request.json)  # Validate incoming data

    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        query = "UPDATE members SET name = %s, email = %s, phone = %s WHERE id = %s"
        cursor.execute(
            query, (member_data["name"], member_data["email"], member_data["phone"], id)
        )
        conn.commit()
        return jsonify({"message": "Order updated successfully"}), 200

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/members/<int:id>", methods=["DELETE"])
def delete_member(id):
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        # query to find order based on their id
        query = "SELECT * FROM members WHERE id = %s"
        # check if order exists in db
        cursor.execute(query, (id,))
        order = cursor.fetchone()
        if not order:
            return jsonify({"error": "Member does not exist"}), 404

        # If customer exists, we shall delete them :(
        del_query = "DELETE FROM members where id = %s"
        cursor.execute(del_query, (id,))
        conn.commit()
        return jsonify({"message": f"Successfully delete id {id}"})

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


############################################################################################################


class workoutSchema(ma.Schema):
    id = fields.Int(dumponly=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    workout_date = fields.Date(required=True)
    member_id = fields.Int(required=True)

    class Meta:
        fields = ("id", "name", "email", "phone", "workout_date", "member_id")


workout_schema = workoutSchema()
workout_schemas = workoutSchema(many=True)


@app.route("/workout", methods=["GET"])
def get_workout():
    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor(dictionary=True)

        query = (
            "SELECT m.*, w.* from members as m join workout as w on m.id = w.member_id"
        )
        cursor.execute(query)
        workout = cursor.fetchall()

        return workout_schemas.jsonify(workout)

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/workout", methods=["POST"])
def post_workout():
    try:
        member_data = member_schema.load(request.json)

    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()

        query = "INSERT INTO members (workout_date, member_id) VALUES (%s,%s)"
        cursor.execute(query, (member_data["workout_date"], member_data["member_id"]))
        conn.commit()
        return jsonify({"message": "Order was successfully added"}), 201

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


@app.route("/workout/<int:id>", methods=["PUT"])
def update_workout(id):
    try:
        # Validate incoming data
        member_data = member_schema.load(request.json)  # Validate incoming data

    except ValidationError as e:
        return jsonify(e.messages), 400

    try:
        conn = connect_db()
        if conn is None:
            return jsonify({"error": "Database connection failed"}), 500
        cursor = conn.cursor()
        query = "UPDATE workout SET workout_date = %s, member_id = %s WHERE id = %s"
        cursor.execute(
            query, (member_data["workout_date"], member_data["member_id"], id)
        )
        conn.commit()
        return jsonify({"message": "Order updated successfully"}), 200

    except Error as e:
        print(f"error: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

    finally:
        # checking again for connection object
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app.run(debug=True)
