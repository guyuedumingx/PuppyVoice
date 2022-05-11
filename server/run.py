#服务器端  
from flask import Flask
from flask import request
from multiprocessing import Process, Queue

app = Flask(__name__)

id_maps = {}

@app.route("/message", methods=["POST"])
def add_msg():
    data = request.form
    if(id_maps.get(data.get("id")) is None):
        id_maps[data.get("id")] = Queue()
    id_maps[data.get("id")].put(data)


@app.route("/message", methods=["GET"])
def custom_msg():
    id = request.args.get("id")
    data = {
        "success": False,
        "msg": ""
    }
    if(id_maps.get(id) is None or id_maps[id].empty()):
        data["msg"] = "没有消息"
    else:
        data["success"] = True
        data["msg"] = id_maps[id].get()
    return data

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8899, debug=True)