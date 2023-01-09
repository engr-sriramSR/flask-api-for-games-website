from pydantic import BaseModel

class PostGame(BaseModel):
    name: str
    link: str
    new: bool
    single_player: bool
    two_player: bool
    multiplayer: bool

class ResponseGamesData(BaseModel):
    name: str
    link: str
    image_name: str
    likes: int
    favorites: int
    if_liked: bool
    if_fav: bool
    comments: list
    count_comments: int
    tag: dict
    image: str

class UpdateGameComments(BaseModel):
    game_name: str
    username: str
    comment: str

class DeleteGameComment(BaseModel):
    game_name: str
    date_time: str


class ResponseUpateGameComments(BaseModel):
    username: str
    comment: str
    if_comment: bool
    datetime: str

class UpdateGameComponents(BaseModel):
    game_name: str

class ResponseUpdateGameLikes(BaseModel):
    game_name: str
    count_likes: int
    if_liked: bool

class ResponseUpdateGameFavorites(BaseModel):
    game_name: str
    count_favorites: int
    if_fav: bool