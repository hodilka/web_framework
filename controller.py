from routing import Route


class Controller:

    @staticmethod
    def index_post(req, msg_assoc = {}):
        if req.method == 'POST':
            print("[SERVER] message recieved: ", msg_assoc)
            return Route.view(req.path.strip("/") + ".html")

    @staticmethod
    def index_get(req, msg_assoc = {}):
        if req.method == 'GET':
                return Route.view(req.path.strip("/") + ".html")