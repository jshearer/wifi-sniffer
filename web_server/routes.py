import flask.ext.restful as rest

class Todos(rest.Resource):

    def get(self):
        """Will give you all the todo items"""
        return {}

    def put(self):
        """Payload contains information to create new todo item"""
        return {}


class TodoItem(rest.Resource):

    def get(self, todo_id):
        """
        Get specific information on a Todo item

        :param todo_id: The Todo Item's ID, which is unique and a primary key
        :type todo_id: int
        """
        return {}
