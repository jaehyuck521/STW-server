from flask import Flask, jsonify, request, current_app, Response, g
from flask.json import JSONEncoder
from sqlalchemy import create_engine, text
import bcrypt
import jwt
from datetime import timedelta,datetime
from functools import wraps

from sqlalchemy.sql.functions import user
def create_app(test_config=None):
    app=Flask(__name__)
    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)
    database=create_engine(app.config['DB_URL'],encoding='utf-8',max_overflow=0)
    app.database=database
    # 회원가입
    @app.route("/sign-up",methods=['POST'])
    def sign_up():
        new_user=request.json
        new_user['password']=bcrypt.hashpw(new_user['password'].encode('UTF-8'),bcrypt.gensalt())
        try:
            new_user_id=app.database.execute(text(""" insert into user ( userid, password,  email, name) values(:userid, :password, :email, :name)"""),new_user).lastrowid
            # row=current_app.database.execute(text("""select userid, name, gender from user where id = :user_id"""),{'user_id':new_user_id}).fetchone()
            # created_user={'userid':row['userid'],'name':row['name'], 'gender':row['gender']} if row else None
            return 'success'
        except: 
            return 'denied'
    @app.route('/login',methods=['POST'])
    def login():
        credential =request.json
        userid=credential['userid']
        password=credential['password']
        row=database.execute(text("""select userid, password from user where userid=:userid"""),{'userid':userid}).fetchone()
        if row and bcrypt.checkpw(password.encode('UTF-8'),row['password'].encode('UTF-8') ):
            userid=row['userid']
            # payload={'userid':userid,'exp':datetime.utcnow()+timedelta(seconds=60 * 60 * 24)}
            # token=jwt.encode(payload, app.config['JWT_SECRET_KEY'],'HS256')
            # return jsonify({'access_token':token.decode('UTF-8')})
            
            return jsonify({'access':userid})
        else:
            return jsonify({'access':"denied"})
    @app.route('/mypage/<userid>',methods=['GET'])
    def mypage(userid):
        try:
            row=database.execute(text("""select userid, email, password, name from user where userid=:userid"""),{'userid':userid}).fetchone()
            return jsonify(row)
        except:
            return "No"

    def login_required(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            access_token=request.headers.get('Authorization')
            if access_token is not None:
                try:
                    payload=jwt.decode(access_token, current_app.config['JWT_SECRET_KEY'],'HS256')
                except jwt.InvalidTokenError:
                    payload=None
                if payload is None: return Response(status=401)
                userid=payload['userid']
                g.userid=userid
                g.user=get_user(userid) if userid else None
            else: 
                return Response(status=401)
            return f(*args, **kwargs)
        return decorated_function
    @app.route('/user/update/<userid>',methods=['POST'])
    def updateuser(userid):
        info=request.json
        nickname=info['name']
        current_app.database.execute(text("""update user set name=:name where userid=:userid"""),{'name':nickname,'userid':userid})
        return nickname,200

    @app.route('/memory/create',methods=['POST'])
    @login_required
    def memory():
        badmemory=request.json
        badmemory['userid']=g.userid
        try:
            current_app.database.execute(text("""insert into badmemory(userid, content,enddate) values(:userid,:content,DATE_ADD(NOW(), INTERVAL 28 DAY))"""),badmemory)
            return '',200     
        except:
            return 'Insert Error',401
    @app.route('/memory/read',methods=['GET'])
    @login_required
    def extractmemory():
        userid=g.userid
        badmemory=current_app.database.execute(text("""select id, userid,content,createdate,enddate from badmemory where userid=:userid"""),{'userid':userid}).fetchall()
        now=datetime.now()
        for row in badmemory:
            etime=str(row['enddate'])
            endtime=datetime.strptime(etime, '%Y-%m-%d %H:%M:%S')
            date_diff=now-endtime
            if(date_diff.days==0):
                id=row['id']
                current_app.database.execute(text("""delete from badmemory where id=:idx"""),{'idx':id})
                return row['content']    
        if badmemory is None:
            return 'Not exist', 401
        else:
            return jsonify(badmemory)
    
    # 개인일기 생성하기 
    @app.route('/diary/create/<userid>',methods=['POST'])
    # @login_required
    def createPersonalDiary(userid):
        pDiary=request.json
        pDiary['userid']=userid
        try:
            current_app.database.execute(text("""insert into pdiary(userid,contents) values(:userid,:contents)"""),pDiary)
            return "success"
        except:
            return "fail"      
    
    # 개인일기 수정하기
    @app.route('/diary/update/<int:id>',methods=['POST'])
    # @login_required
    def updatePersonalDiary(id):
        modi=request.json
        newcontent=modi['contents']
        try:
            current_app.database.execute(text("""update pdiary set contents=:content where  id=:id"""),{'content':newcontent,'id':id})
            return 'success'
        except:
            return 'Fail'
    
    # 개인일기 지우기
    @app.route('/diary/delete/<int:id>',methods=['POST'])
    # @login_required
    def deletePersonalDiary(id):
        try:
            current_app.database.execute(text("""delete from pdiary where id=:id"""),{'id':id})
            return 'success'
        except:
            return 'fail'
    
    # 공동일기 만들기
    @app.route('/diary/commoncreate/<userid>',methods=['POST'])
    # @login_required
    def createCommonDiary(userid):
        userid=userid
        comdiary=request.json
        try:
            diary_key=current_app.database.execute(text("""insert into commondiary(ccontents,host,title) values(:contents,:userid,:title)"""),{'contents':comdiary['ccontents'],'userid':userid,'title':comdiary['title']}).lastrowid
            current_app.database.execute(text("""insert into commonuser(userid,diary_id) values(:userid,:diary_num)"""),{'userid':userid,'diary_num':diary_key})
            return 'success'
        except:
            return 'failed'
    
    # 공동일기에 사용자 초대하기
    @app.route('/diary/invite/<int:diarynum>',methods=['POST'])
    # @login_required
    def inviteCommonDiary(diarynum):
        # userid=g.userid
        invite=request.json
        try:
            current_app.database.execute(text("""insert into commonuser(userid,diary_id) values(:userid,:diary_num)"""),{'userid':invite['invite'],'diary_num':diarynum})
            return 'success'
        except:
            return 'failed'
    # 공동일기 수정하기
    @app.route('/diary/updatecommon/<id>',methods=['POST'])
    # @login_required
    def updateCommondiary(id):
        ncontent=request.json
        newcontent=ncontent['content']
        try:
            current_app.database.execute(text("""update commondiary set ccontents=:new where id=:id"""),{'new':newcontent,'id':id})
            return  'success'
        except:
            return 'failed'
    
    # 개인일기 다 읽기
    @app.route('/diary/read/<userid>',methods=['GET'])
    # @login_required
    def readAllpDiary(userid):
        userid=userid
        try:
            personalList=current_app.database.execute(text("""select * from pdiary where userid=:uid"""),{'uid':userid}).fetchall()
            return jsonify(personalList)
        except:
            return "no data"
    
    # 공동 일기 데이터 지우기
    @app.route('/diary/deletecommon/<int:id>',methods=['POST'])
    @login_required
    def deleteCommon(id):
        # try:
        current_app.database.execute(text("""delete  from commondiary where id=:id"""),{'id':id})
        current_app.database.execute(text("""delete  from commonuser where diary_id=:id"""),{'id':id})
        return '', 200
        # except:
        #     return 'Delete Failed',401
    @app.route("/ping",methods=['GET'])
    def ping():
        return "pong"

    # 공동일기 다 읽어오기 
    @app.route('/diary/readC/<userid>',methods=['GET'])
    # @login_required
    def readAllcDiary(userid):
        userid=userid
        try:
            commonList=current_app.database.execute(text("""select commondiary.id, commondiary.ccontents, commondiary.create_at, commondiary.host, commondiary.title from commondiary,commonuser where commondiary.id=commonuser.diary_id and commonuser.userid=:user"""),{'user':userid}).fetchall()
            return jsonify(commonList)
        except:
            return "no data"

    @app.route("/diary/commonlist",methods=['GET'])
    def listcommon():
        try:
            sharedlist=current_app.database.execute(text("""select id, create_at, host, ccontents, title from commondiary""")).fetchall()
            return jsonify(sharedlist)
        except:
            return "no commondiary"
    @app.route("/chatpredict",methods=['POST'])
    def chat():
        chat=request.json
        try:
            return jsonify()

        except:
            return "null"
    @app.route("/emotionpredict",methods=['POST'])
    def emotion():
        emoji=request.json
        try:
            return jsonify()
        except:
            return "null"


    



    




    



        

    return app




# Test   
app=create_app()


def get_user(user_id):
    user=current_app.database.execute(text("""select userid,name, email, gender from user where userid=:userid"""),{'userid':user_id}).fetchone()
    return {
            'userid':user['userid'],
            'name' : user['name'],
            'email':user['email'],
            'gender':user['gender']
     } if user else None


@app.route("/tweet",methods=['POST'])
def tweet():
    payload=request.json
    user_id=int(payload['id'])
    tweet=payload['tweet']
    if user_id not in app.users:
        return "사용자가 존재하지 않습니다",400
    if len(tweet)>300:
        return "300자를 초과했습니다.",400
    user_id=int(payload['id'])
    app.tweets.append({
        'user_id':user_id,
        'tweet':tweet
    })
    return '', 200

@app.route("/follow",methods=['POST'])
def follow():
    payload=request.json
    user_id=int(payload['id'])
    user_id_to_follow=int(payload['follow'])
    if user_id not in app.users or user_id_to_follow not in app.users:
        return "사용자가 존재하지 않습니다.",400
    
    user=app.users[user_id]
    user.setdefault('follow',set()).add(user_id_to_follow)
    return jsonify(user)

class CustomJSONEncoder(JSONEncoder): # 상속을 받는다. 
    def default(self,obj):
        if isinstance(obj,set): # set인 경우, list로 변경해준다. 
            return list(obj)
    
        return JSONEncoder.default(self, obj) # set이 아닌 경우, 본래 클래스의 default를 호출해서 return. 

app.json_encoder=CustomJSONEncoder # 클래스를 json 인코더로 지정해준다. jsonify 호출될 때, 이 클래스 사용한다. 

@app.route("/unfollow",methods=['POST'])
def unfollow():
    payload=request.json
    user_id=int(payload['id'])
    user_id_to_follow=int(payload['unfollow'])
    if user_id not in app.users or user_id_to_follow not in app.users:
        return "사용자가 존재하지 않습니다.",400
    
    user=app.users[user_id]
    user.setdefault('follow',set()).discard(user_id_to_follow) # discard는 삭제하고자 하는 값이 없어도 무시한다. remove를 안 쓴다. 있는 지 확인안해도 되서 편함.
    return jsonify(user)

@app.route('/timeline/<int:user_id>',methods=['GET']) # 사용자의 아이디 지정할 수 있게끔.
def timeline(user_id):
    if user_id not in app.users:
        return "사용자가 존재하지 않습니다.",400
    
    follow_list=app.users[user_id].get('follow',set()) # 팔로우한 사용자들을 가져온다. 
    follow_list.add(user_id) # 사용자 id도 추가. 
    timeline=[tweet for tweet in app.tweets if tweet['user_id'] in follow_list] # 전체 트윗중 팔로우하는 사람들 트윗 읽어옴. 
    return jsonify({ # 아이디와 함께 타임라인 json형태로 리턴. 
        'user_id': user_id,
        'timeline':timeline
    })

