
import users_db
from flask import Blueprint,jsonify,request
user = Blueprint('/user',__name__)
# router.get("/api/user", this.getUser);
#         router.get("/api/user/all", this.getAllUsers);
#         router.post("/api/user", this.addUser);
#         router.post("/api/user/update", this.updateUser);
#         router.post("/api/user/remove", this.removeUser);
#TODO 异常处理
@user.route('/add', methods=['POST'])
def add():
    data = request.json
    print( data )
    params = data["options"]
    res=users_db.users_add(params)
    return jsonify({ "success": True,"result":res,"error":''})



@user.route('/all', methods=['GET'])
def get_users_all():
    res=users_db.users_all_valid()
    return jsonify({ "success": True,"result":res})


@user.route('/update', methods=['POST'])
def update():
    data = request.json
    print( data )
    params = data["options"]
    res=users_db.users_update(params)
    return jsonify({ "success": True,"result":res})

@user.route('/remove', methods=['POST'])
def remove():
    data = request.json
    print( data )
    params = data["options"]
    res=users_db.users_remove(params)
    return jsonify({ "success": True,"result":res})
