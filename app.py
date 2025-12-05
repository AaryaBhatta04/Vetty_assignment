from flask import Flask,request,jsonify
import requests

app=Flask(__name__)
BASE="https://api.coingecko.com/api/v3/"  # Obtained from the website given in the assignment sheet

def coingecko(path,params=None):
    r=requests.get(BASE+path,params=params,timeout=10)
    r.raise_for_status()
    return r.json()

@app.route("/api/coins")
def coins():
    return jsonify(coingecko("/coins/list"))

@app.route("/api/categories")
def categories():
    return jsonify(coingecko("/coins/categories"))

@app.route("/api/coins/filter")
def filter_coins():
    ids=request.args.get("ids")
    category_param=request.args.get("category")
    
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
    
    return jsonify(output)
    
if __name__=="__main__":
    app.run(port=5000,debug=True)