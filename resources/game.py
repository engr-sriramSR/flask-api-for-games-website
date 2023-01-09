from flask import request
from flask_smorest import Blueprint, abort
from db import mongodb
from flask_jwt_extended import  jwt_required, get_jwt_identity
from models import PostGame, ResponseGamesData, UpdateGameComments, ResponseUpateGameComments, UpdateGameComponents, ResponseUpdateGameFavorites, ResponseUpdateGameLikes, DeleteGameComment
from flask_pydantic import validate
from datetime import datetime
from db import grid_fs
import codecs

blp = Blueprint("games", __name__, description="Games blueprint.")

class RequiredError(Exception):
    pass

@blp.route("/game/add", methods=["POST"])
@jwt_required()
@validate()
def add_game(form: PostGame):
    try:
        games_collection = mongodb.db.games_data
        title = form.name
        link = form.link
        user_id = get_jwt_identity()
        if link == None or len(link) <= 0 or title == None or len(title) <= 0:
            raise RequiredError()
        try:
            image = request.files["game_thumbnail"]
        except:
            raise RequiredError()
        games_collection.create_index("link", unique=True)
        games_collection.insert_one({
            "_id": title,
            "user_id": user_id,
            "link": link,
            "image_name": title + ".png",
            "likes": [],
            "favorites": [],
            "comments": [],
            "tag": {
                "new": form.new,
                "single_player": form.single_player,
                "two_player": form.two_player,
                "multiplayer": form.multiplayer
            }
        })
        grid_fs.put(image, filename = title + ".png")
    except RequiredError:
        abort(400, message="All required fields should be given.")
        
    except Exception as e:
        if(e.code == 11000) and e.details["keyValue"] == {"_id": title}:
            abort(400, message="Game with that name already excists.")
        elif (e.code == 11000) and e.details["keyValue"] == {"link": link}:
            abort(400, message = "The Link already excists.")
        else:
            abort(404, message="Failed.")

    return {"message": "Game uploaded successfully."}, 201

@blp.route("/games", methods=["GET"])
@jwt_required()
@validate(response_many=True, on_success_status=200)
def get_games():
    try:
        games_collection = mongodb.db.games_data
        games = games_collection.find()
        user_id = get_jwt_identity()
        res = []
        for game in games:
            if user_id in game["likes"]:
                if_liked = True
            else:
                if_liked = False
            if user_id in game["favorites"]:
                if_fav = True
            else:
                if_fav = False
            if len(game["comments"]) > 0:
                comment_array = []
                for comment in game["comments"]:
                    if comment["user_id"] == user_id:
                        if_comment = True
                    else:
                        if_comment = False
                    comment_response = {
                        "username": comment["name"],
                        "comment": comment["comment"],
                        "datetime": comment["datetime"],
                        "if_comment": if_comment
                    }
                    comment_array.append(comment_response)
            else:
                comment_array = []
            image_file = grid_fs.find_one({"filename": game["_id"] + ".png"})
            base64_data = codecs.encode(image_file.read(), 'base64')
            image = base64_data.decode('utf-8')
            res.append(ResponseGamesData(
                name=game["_id"], 
                link=game["link"],
                image_name=game["image_name"], 
                likes = len(game["likes"]),
                favorites = len(game["favorites"]),
                if_liked=if_liked,
                if_fav=if_fav,
                comments=comment_array,
                count_comments=len(game["comments"]),
                tag=game["tag"],
                image=image
                ))
    except:
        abort(404, message="Failed.")
    
    return [game for game in res]

@blp.route("/games/<string:game_name>/delete", methods=["DELETE"])
@jwt_required()
@validate()
def delete_game(game_name):
    games_collection = mongodb.db.games_data
    game = games_collection.find_one({"_id": game_name})
    user_id = get_jwt_identity()
    if game["user_id"] == user_id:
        image_name = game["image_name"]
        image_file = mongodb.db.fs.files
        image_chunk = mongodb.db.fs.chunks
        image = image_file.find_one({"filename": image_name})
        files_id = image["_id"] 
        image_chunk.delete_many({"files_id": files_id})
        image_file.delete_one({"filename": image_name})
        games_collection.delete_one({"_id": game_name})
        return {"message": "Game deleted successfully."}
    else:
        abort(401, message="Only the game owner can delete the game.")

@blp.route("/comments", methods=["PUT"])
@jwt_required()
@validate()
def update_comments(body: UpdateGameComments):
    try:
        games_collection = mongodb.db.games_data
        now = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        user_id = get_jwt_identity()
        comment = {"user_id": user_id,"name": body.username, "comment": body.comment, "datetime": now}
        games_collection.update_one({"_id":body.game_name}, {"$push":{"comments": comment}})
    except:
        abort(400, message="Failed.")

    return ResponseUpateGameComments(username=body.username, comment=body.comment, if_comment=True, datetime=now)

@blp.route("/comment/delete", methods=["DELETE"])
@jwt_required()
@validate()
def delete_comment(body: DeleteGameComment):
    games_collection = mongodb.db.games_data
    game = games_collection.find_one(body.game_name)
    user_id = get_jwt_identity()
    for comment in game["comments"]:
        if comment["datetime"] == body.date_time and comment["user_id"] == user_id:
            game["comments"].remove(comment)
            games_collection.update_one({"_id": body.game_name}, {"$set": {"comments": game["comments"]}})
            return {"messsage": "Comment removed successfully."}
    abort(401, message="Only commented person can delete the comment.")

@blp.route("/likes", methods=["PUT"])
@jwt_required()
@validate()
def update_details(body: UpdateGameComponents):
    try:
        print(body.game_name)
        games_collection = mongodb.db.games_data
        game = games_collection.find_one({"_id": body.game_name})
        user_id = get_jwt_identity()
        if user_id in game["likes"]:
            game["likes"].remove(user_id)
            if_liked = False
            games_collection.update_one({"_id": body.game_name}, {"$set":{"likes": game["likes"]}})
        else:
            game["likes"].append(user_id)
            if_liked = True
            games_collection.update_one({"_id":body.game_name}, {"$set":{"likes": game["likes"]}})
    except:
        abort(400, message="Failed.")

    return ResponseUpdateGameLikes(game_name=body.game_name, count_likes=len(game["likes"]), if_liked=if_liked)

@blp.route("/favorites", methods=["PUT"])
@jwt_required()
@validate()
def update_details(body: UpdateGameComponents):
    try:
        games_collection = mongodb.db.games_data
        game = games_collection.find_one({"_id": body.game_name})
        user_id = get_jwt_identity()
        if user_id in game["favorites"]:
            game["favorites"].remove(user_id)
            if_fav = False
            games_collection.update_one({"_id": body.game_name}, {"$set":{"favorites": game["favorites"]}})
        else:
            game["favorites"].append(user_id)
            if_fav = True
            games_collection.update_one({"_id":body.game_name}, {"$set":{"favorites": game["favorites"]}})
    except:
        abort(400, message="Failed.")

    return ResponseUpdateGameFavorites(game_name=body.game_name, count_favorites=len(game["favorites"]), if_fav=if_fav)

@blp.route("/my-likes", methods=["GET"])
@jwt_required()
@validate(response_many=True, on_success_status=200)
def get_my_like_games():
    try:
        games_collection = mongodb.db.games_data
        games = games_collection.find()
        user_id = get_jwt_identity()
        my_games = []
        for game in games:
            if user_id in game["likes"]:
                my_games.append(ResponseGamesData(
                    name=game["_id"], 
                    link=game["link"],
                    image_name=game["image_name"],
                    likes = len(game["likes"]),
                    favorites = len(game["favorites"]),
                    comments=game["comments"],
                    count_comments=len(game["comments"])))
    except:
        abort(400, message="Failed.")
        
    return [game for game in my_games]

@blp.route("/my-favorites", methods=["GET"])
@jwt_required()
@validate(response_many=True, on_success_status=200)
def get_my_like_games():
    try:
        games_collection = mongodb.db.games_data
        games = games_collection.find()
        user_id = get_jwt_identity()
        my_games = []
        for game in games:
            if user_id in game["favorites"]:
                my_games.append(ResponseGamesData(
                    name=game["_id"], 
                    link=game["link"],
                    image_name=game["image_name"],
                    likes = len(game["likes"]),
                    favorites = len(game["favorites"]),
                    comments=game["comments"],
                    count_comments=len(game["comments"])))
    except:
        abort(400, message="Failed.")
        
    return [game for game in my_games]