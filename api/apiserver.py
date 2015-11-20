#!flask/bin/python

"""Alternative version of the ToDo RESTful server implemented using the
Flask-RESTful extension."""


from flask import Flask, jsonify, abort, make_response
from flask.ext.restful import Api, Resource, reqparse, fields, marshal
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__, static_url_path="")
api = Api(app)

client = MongoClient('db', 27017)
db = client.taskdb


task_fields = {
    'title': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    'uri': fields.Url('task')
}


class TaskListAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided',
                                   location='json')
        self.reqparse.add_argument('description', type=str, default="",
                                   location='json')
        super(TaskListAPI, self).__init__()

    def get(self):
        mytasks = []
        cursor = db.tasks.find()
        for document in cursor:
	    task = {}
	    task['id'] = str(document.get('_id'))
	    task['title'] = document.get('title').encode('utf-8') 
	    task['description'] = document.get('description').encode('utf-8') 
	    task['done'] = document.get('done')
            mytasks.append(task)
        return {'tasks': marshal(mytasks, task_fields)} 

    def post(self):
        args = self.reqparse.parse_args()
        task = {
            'title': args['title'],
            'description': args['description'],
            'done': False
        }
        creationId = db.tasks.save(task)
        task['id'] = str(creationId)
        return {'task': marshal(task, task_fields)}, 201


class TaskAPI(Resource):

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, location='json')
        self.reqparse.add_argument('description', type=str, location='json')
        self.reqparse.add_argument('done', type=bool, location='json')
        super(TaskAPI, self).__init__()

    def get(self, id):
        task = db.tasks.find_one({"_id": ObjectId(id)})
        task['id'] = str(task['_id'])
        task.pop('_id')
        if len(task) == 0:
            abort(404)
        return {'task': marshal(task, task_fields)}

    def put(self, id):
        etask = db.tasks.find_one({"_id": ObjectId(id)})
        if len(etask) == 0:
            abort(404)
        task = {}
        tempid = str(etask['_id']) 
        etask.pop('_id')
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                task[k] = v
        db.tasks.update({ "_id" : ObjectId(id)}, {'$set': task})
        # Final state for that objectId, find_one should not be used in order
        # to detect duplicates.
        result = db.tasks.find_one({"_id": ObjectId(id)})
        result['id'] = str(result['_id'])
        result.pop('_id')
        return {'task': marshal(result, task_fields)}

    def delete(self, id):
        if len(id) == 0:
            abort(404)
        db.tasks.remove({'_id':ObjectId(id)})
        return {'result': True}


api.add_resource(TaskListAPI, '/todo/api/v1.0/tasks', endpoint='tasks')
api.add_resource(TaskAPI, '/todo/api/v1.0/tasks/<string:id>', endpoint='task')


if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)
