import os
import requests
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

API_URL = os.environ.get("API_URL")
PORT = os.environ.get("PORT")

app = Flask(__name__)
CORS(app)

@app.route('/search', methods = ['GET'])
def getComments():
    params = request.args.to_dict()
    search_author = params.get("search_author")
    params.pop("search_author", None)
    date_range_start = params.get("at_from")
    params.pop("at_from", None)
    date_range_end = params.get("at_to")
    params.pop("at_to", None)
    like_range_start = params.get("like_from")
    params.pop("like_from", None)
    like_range_end = params.get("like_to")
    params.pop("like_to", None)
    reply_range_start = params.get("reply_from")
    params.pop("reply_from", None)
    reply_range_end = params.get("reply_to")
    params.pop("reply_to", None)
    search_text = params.get("search_text")
    params.pop("search_text", None)

    if len(params.keys()) > 0:
        error = {
            "error": "Invalid Parameters",
            "parameters": [f"Invalid parameter: {i}" for i in params.keys()]
        } 
        response = jsonify(error)
        return response, 400

    data = requests.get(API_URL).json()

    result = []

    for comment in data["comments"]:
        try :
            if like_range_start != None and int(like_range_start) > comment.get("like"):
                continue
            if like_range_end != None and int(like_range_end) < comment.get("like"):
                continue
            if reply_range_start != None and int(reply_range_start) > comment.get("reply"):
                continue
            if reply_range_end != None and int(reply_range_end) < comment.get("reply"):
                continue

        except ValueError:
            error = {
                "error": "Bad Request",
                "message": "Please enter valid input!" 
            }
            response = jsonify(error)
            return response, 400
        

        comment_date = datetime.strptime(" ".join(comment.get("at").split()[1:4]), "%d %b %Y")

        try:
            if date_range_start != None:
                start_date = datetime.strptime(date_range_start, "%d-%m-%Y")
                if start_date != None and comment_date < start_date:
                    continue
            if date_range_end != None:
                end_date = datetime.strptime(date_range_end, "%d-%m-%Y")
                if end_date != None and comment_date > end_date:
                    continue

        except ValueError:
            error = {
                "error": "Bad Request",
                "message": "Please enter valid input!" 
            }
            response = jsonify(error)
            return response, 400

        if search_author != None and comment.get("author").find(search_author) == -1:
            continue
        if search_text != None and comment.get("text").find(search_text) == -1:
            continue

        result.append(comment)

    data = {
        "number_of_comments": len(result),
        "comments": result
    }
    response = jsonify(data)
    return response, 200

if __name__ == "__main__":
    app.run(debug=False, port=PORT)