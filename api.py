from fastapi import FastAPI, Header,Depends, Request
#reqiuires Python 3.9.6 from typing_extensions import Annotated 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from functools import wraps

import uvicorn

from dotenv import load_dotenv
load_dotenv()

from db import list_products, insert_new_product, delete_product, insert_new_user, login_user, get_current_user, get_current_active_user

from models import Products, Users

from pydantic import BaseModel

from typing import Optional



# initialize API
app = FastAPI()

#this class below is a fastAPI orbject and NOT a sqlAlchemy object
class ProductsInput(BaseModel):
    product_id: str
    product_name: str
    product_description: str
    product_price: float

#this class below is a fastAPI orbject and NOT a sqlAlchemy object
class UsersInput(BaseModel):
    user_fullname: Optional[str]
    user_email: str
    user_password: str

class LoginOutput(BaseModel):
    access_token: str
    token_type: str="Bearer"
    message: str


def auth_required(func):
    @wraps(func)
    # we need the wraps so we can accesss the parameters provided in the "router"
    def wrapper(request: Request, *args, **kwargs):
        #print(f"val of access token=|{request.headers.get('access-token')}|")
        current_user: UsersInput = get_current_user(request.headers.get('access-token'))
        if(current_user and current_user.user_password):
            return func(request=request, *args, **kwargs)
    return wrapper




@app.get('/')
def get_func():
    return {'text': 'hello world'}, 200

#will convert auth funciton into decorator later

@app.get('/products')
#def get_products(access_token: str=Header(None)):
# requires Python 3.9.6 def get_products(current_user: Annotated[UsersInput, Depends(get_current_active_user)]):

#def get_products(current_user: UsersInput = Depends(get_current_active_user)):    
@auth_required
#def get_products():    
def get_products(request: Request):    
    #print(f"val of access token=|{current_user.user_email}|")
#    print(f"val of access token=|{access_token}|")
#    if(access_token):
#        current_user=get_current_user(access_token)
#        if(current_user and current_user.user_password):
#            my_prods = list_products()
#            return my_prods
#        else: return []    
#    else: return []
    #if(current_user and current_user.user_password):
    #    my_prods = list_products()
    #    return my_prods
    #else: return []    
    my_prods = list_products()
    return my_prods


@app.post('/products',status_code=201)
@auth_required
def create_products(request: Request, input: ProductsInput):
    try:
        #convert our requets object into a model object which is a SQl-Alcehmy object
        new_product = Products(product_id=input.product_id, product_name=input.product_name, product_price=input.product_price, product_description=input.product_description)

        insert_new_product([new_product])
        return "product inserted successfully"
    except:
        return "product failed to insert"


@app.delete('/products/{product_id}',status_code=202)
@auth_required
def delete_products(request: Request, product_id: str):
    try:
        result = delete_product(product_id)
        if(result): return "product deleted successfully"
        return "product not found"
    except: 
        return "something went wrong,connection of server error ", 500


#---------------------------------
#THIS IS FOR UPWORK PROJECT : 
#Python Developer Needed to Build Authentication Service using FastAPI and PostgreSQL 

@app.post('/signup',status_code=201)
def user_signup(input: UsersInput):
    try:
        #convert our requets object into a model object which is a SQl-Alcehmy object
        new_user = Users(user_fullname=input.user_fullname, user_email=input.user_email, user_password=input.user_password)

        insert_new_user([new_user])
        return "User registered/inserted successfully"
    except Exception as e:    
        return f"User failed to be registered/insertedi and error = |{e}|"
    ############ COMING, we will do the sending of the email soon    


@app.post('/signin',status_code=200,response_model=LoginOutput) #2000 because we are not creating/inserting anything
## requires Python 3.9.6 def user_signin(input: Annotated[OAuth2PasswordRequestForm, Depends()]):    
def user_signin(input: UsersInput):
    try:
        #convert our requets object into a model object which is a SQl-Alcehmy object
        new_user = Users(user_email=input.user_email, user_password=input.user_password)

        access_token = login_user(new_user)
        if(access_token): 
            return {'access_token':access_token,'message':"User Logged in successfully"}
        else: return {'access_token':"",'message':"User Credentials provided do not match"}
    except Exception as e:    
        return {'access_token':"",'message':f"User failed to be logged-in and error = |{e}|"}




