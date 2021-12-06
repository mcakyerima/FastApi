from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from typing import Optional
from random import randrange
import psycopg2
# import RealDictCursor to enable us see column names
from psycopg2.extras import RealDictCursor
import time


app = FastAPI()

# creating a shceema for our data with pydantic


class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None


# connecting to the database using psycopg2
while True:
    try:

        conn = psycopg2.connect(host='localhost', database="fastApi", user='postgres',
                                password='Mcakyerima1', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection to Database was established")
        break
    except Exception as error:
        print("Failed to connect to Database")
        print("Error", error)
        time.sleep(2)


my_posts = [{"title": "My first Api with fast Api", "content": "Fast api is an amazing framework for building api's", "id": 1},
            {"title": "Making Tea", "content": "To make a tea, we boil a hot water and put a teabag and sugar", "id": 2}]

# create a function for getting post by id


def get_post_by_id(id):
    for post in my_posts:
        if post['id'] == id:
            return post

# get post index by id for post deletions


def get_post_index(id):
    for index, post in enumerate(my_posts):
        if post['id'] == id:
            return index


# creating a get method is as simple as putting a decorator and then instanciating the app class with the request type
@app.get('/')
async def root():
    return {'message': "Welcome to Fast Api"}


# creating another get mothod and setting a different path for
@app.get('/posts')
def post():
    # execute and sql statement using the cursor instance u created
    cursor.execute(""" SELECT * FROM posts """)
    # save result of query to variable
    post = cursor.fetchall()
    print(post)
    return {"data": post}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def chat_post(post: Post):
    # inserting post into database
    cursor.execute(""" INSERT INTO posts (title , content, published) VALUES (%s, %s, %s) RETURNING * """,
                    (post.title, post.content,post.published))
    #fetch value that is returned from insert with cursor.fetchone() Function and save it to a viariable
    new_post = cursor.fetchone()
    # commit the insert by commiting the conn in order to save to database
    conn.commit()
    return {"data": new_post}

 # getting  post by id with fast Api


@app.get("/posts/{id}")
def get_post_(id: int):
    cursor.execute(""" SELECT * FROM posts WHERE id = (%s)""",(str(id),))
    post = cursor.fetchone() 
    if not post:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"your post with id: {id} was not found")
    return {"post": post}

# deleting post by id


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(""" DELETE FROM posts WHERE id = %s RETURNING * """, (str(id),))
    deleted_post = cursor.fetchone()
    conn.commit()
    # get the index of the post
    # send error if post with id does not exist
    if not deleted_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# updating post by put


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    index = get_post_index(id)
    # send error if post with id does not exist
    if index == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    # convert the post from front-end to a dictionary and save it in a variable post_dict
    post_dict = post.dict()
    # insert the id recieved from front end to post_dict since it has No id
    post_dict['id'] = id
    # goto the index from my_post and updata my_posts with the new post
    my_posts[index] = post_dict
    return {"message": "post updated successfully"}
