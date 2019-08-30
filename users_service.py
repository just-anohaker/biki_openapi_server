
import users_db
from flask import Blueprint,jsonify,request
user = Blueprint('/api/user',__name__)
# router.get("/api/user", this.getUser);
#         router.get("/api/user/all", this.getAllUsers);
#         router.post("/api/user", this.addUser);
#         router.post("/api/user/update", this.updateUser);
#         router.post("/api/user/remove", this.removeUser);
#TODO 异常处理
@user.route('', methods=['POST'])
def add():
    try:
        data = request.json
        print( data )
        params = data #data["options"]
        res=users_db.users_add(params)
    except Exception as err:
            return jsonify({ "success": False,"error":str(err)})
    return jsonify({ "success": True,"result":res})




@user.route('/all', methods=['GET'])
def get_users_all():
    res=users_db.users_all_valid()
    return jsonify({ "success": True,"result":res})


@user.route('/update', methods=['POST'])
def update():
    data = request.json
    print( data )
    params = data["options"]
    userid = data["userId"]
    params['userId'] = userid
    res=users_db.users_update(params)
    return jsonify({ "success": True,"result":res})

@user.route('/remove', methods=['POST'])
def remove():
    data = request.json
    print( data )
    params = data["userId"]
    res=users_db.users_remove(params)
    return jsonify({ "success": True,"result":res})
