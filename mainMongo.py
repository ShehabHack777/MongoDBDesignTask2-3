from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from typing import List,Annotated,Optional
import motor.motor_asyncio as aiomotor
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, BeforeValidator

PyObjectId = Annotated[str, BeforeValidator(str)]



app = FastAPI()

# Connect to MongoDB
client = aiomotor.AsyncIOMotorClient("mongodb://localhost:27017")
db = client.mydatabase
players_collection = db.players



class Player(BaseModel):
    _id: Optional[PyObjectId] = Field(default=ObjectId ,alias="_id")
    uuid: str =Field(default_factory=None)
    username: str = Field(..., min_length=1, max_length=30)
    score: int = Field(..., gt=0)
    inventory: dict = Field({}, example={"items": []})
    
    # class Config:
    #     allow_population_by_field_name = True
    #     arbitrary_types_allowed = True #required for the _id 
    #     # json_encoders = {ObjectId: str}
Player.__config__ = {"use_dict": True}


@app.get("/players/", response_model=List[Player])
async def get_players():
    cursor = players_collection.find()
    players = await cursor.to_list(length=100)
    # print(Player(**players[0]))

    # print(players)
    if players:
        for player in players:
            # print(player["_id"])
            player["uuid"] = str(player["_id"])
        print(players)
        
        
        return players
    else:
        return  {"message":"No Players Found"}

@app.post("/players/", response_model=Player)
async def create_player(player: Player):
    # current_datetime = datetime.now()
# Convert datetime to timestamp
    # timestamp = current_datetime.timestamp()
    player_dict = player.dict()
    print(player)
    # player_dict["_id"] = str(player_dict["_id"])
    await players_collection.insert_one(player_dict)
 
    return player_dict

@app.get("/players/{player_id}", response_model=Player)
async def get_player(player_id: str):
    player = await players_collection.find_one({ "_id":ObjectId( player_id) })
    if player:
       
        return Player( player)
    else:
        return  {"Message":"No such players"}

# @app.put("/players/{player_id}", response_model=Player)
# async def update_player(player_id: str, player: Player):
#     result = await players_collection.replace_one({ "_id": player_id }, player.dict())
#     if result:
#         return player
#     else:
#         raise HTTPException(status_code=404, detail="Player not found")

@app.delete("/players/{player_id}")
async def delete_player(player_id: str):
    print(type(player_id))
    
    result = await players_collection.delete_one({ "_id": ObjectId( player_id)})
    print(result)
    if result:
        return {"message": "Player deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Player not found")