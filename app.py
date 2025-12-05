from flask import Flask,request,jsonify
import requests
import os
import jwt
from functools import wraps
from datetime import datetime, timedelta

app=Flask(__name__)
BASE="https://api.coingecko.com/api/v3"  # Obtained from the website given in the assignment sheet

JWT_SECRET = os.environ.get("JWT_SECRET", "e4f7c2b91f3a4d7e8b2a6f915c3d98f04b7e6d2a1f9c4e3d8a0b6c2d3f7e9a1b")
JWT_ALGO="HS256"
JWT_EXP_MINUTES=60

USERS={"Aaryaman Bhattacharya": "Aaryaman@04"}

def coingecko(path,params=None):
    r=requests.get(BASE+path,params=params,timeout=10)
    r.raise_for_status()
    return r.json()

def get_page():
    try:
        page_num=int(request.args.get("page_num",1))
    except (TypeError,ValueError):
        page_num=1
    try:
        per_page=int(request.args.get("per_page",10))
    except (TypeError,ValueError):
        per_page=10
    
    return page_num,per_page

def paginate(items,page_num,per_page):
    total_items=len(items)
    total_pages=(total_items+per_page-1)//per_page
    start=(page_num-1)*per_page
    end=start+per_page
    page_items=items[start:end]
    return{
        "page_num":page_num,
        "per_page":per_page,
        "total_items":total_items,
        "total_pages":total_pages,
        "items":page_items
    }

def create_token(username):
    now=datetime.utcnow()
    payload={
        "sub":username,
        "iat":now,
        "exp":now+timedelta(minutes=JWT_EXP_MINUTES)
    }
    token=jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGO)
    
    if isinstance(token,bytes):
        token=token.decode("utf-8")
    return token

def decode_token(token):
    return jwt.decode(token,JWT_SECRET,algorithms=[JWT_ALGO])

def require_jwt(f):
    @wraps(f)
    def wrapper(*args,**kwargs):
        auth=request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return jsonify({"error":"Either Authorization header is missing or it should be like: Bearer <token>"}),401
        token=auth.split(" ",1)[1].strip()
        try:
            payload=decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error":"token expired"}),401
        except jwt.InvalidTokenError:
            return jsonify({"error":"invalid token"}),401
        
        request.user=payload.get("sub")
        return f(*args,**kwargs)
    return wrapper


@app.route("/auth/login",methods=["POST"])
def login():
    # expects JSON: {"username": "...", "password": "..."}
    data=request.get_json(silent=True) or {}
    username=data.get("username")
    password=data.get("password")
    if not username or not password:
        return jsonify({"error":"username and password required"}),400
    expected=USERS.get(username)
    if expected is None or expected != password:
        return jsonify({"error":"Wrong Credentials"}),401
    token=create_token(username)
    return jsonify({"token":token})

@app.route("/api/coins")
@require_jwt
def coins():
    # return jsonify(coingecko("/coins/list")) -> This was before pagination
    page_num,per_page=get_page()
    coins=coingecko("/coins/list")
    return jsonify(paginate(coins,page_num,per_page))

@app.route("/api/categories")
@require_jwt
def categories():
    # return jsonify(coingecko("/coins/categories")) -> This was before pagination
    page_num,per_page=get_page()
    cats=coingecko("/coins/categories")
    return jsonify(paginate(cats,page_num,per_page))

@app.route("/api/coins/filter")
@require_jwt
def filter_coins():
    ids=request.args.get("ids")
    category_param=request.args.get("category")
    
    page_num,per_page=get_page()
    
    categories=[]
    if category_param:
        for category in category_param.split(","):
            category=category.strip()
            if category:
                categories.append(category)

    params_common={}
    if ids:
        params_common["ids"]=ids
    
    def dothing(currency):
        results=[]
        if categories:
            for category in categories:
                results.extend(coingecko("/coins/markets",{** params_common, "category":category,"vs_currency":currency}))
        else:
            results=coingecko("/coins/markets",{**params_common,"vs_currency":currency})

        return results

    rupee_list=dothing("inr")
    canada_list=dothing("cad")
    
    rupee_map={}
    for it in rupee_list:
        rupee_map.setdefault(it["id"],it)
    
    canada_map={}
    for it in canada_list:
        canada_map.setdefault(it["id"],it)
        
    all_ids=sorted(set(rupee_map)|set(canada_map))
    
    output=[]
    
    for id in all_ids:
        chk=rupee_map.get(id) or canada_map.get(id)
        output.append({
            "id":id,
            "symbol":chk.get("symbol"),
            "name":chk.get("name"),
            "in rupees":rupee_map.get(id),
            "in canadian":canada_map.get(id),
        })
    
    return jsonify(paginate(output,page_num,per_page))
    
if __name__=="__main__":
    app.run(port=5000,debug=True)