from routing import Route


class Controller:

    def __init__(self):
        self.body_of_the_sendback = {}

    def index_post(self, req, msg_assoc = {}):
        print("[SERVER] message recieved: ", msg_assoc)
        self.body_of_the_sendback['body'] = Route.view(req.path.strip("/") + ".html")
        return self.body_of_the_sendback

    def index_get(self, req, msg_assoc = {}):
        print('[SERVER] message recieved: ', msg_assoc)
        self.body_of_the_sendback['body'] = Route.view(req.path.strip("/") + ".html")
        self.redirect('/')
        return self.body_of_the_sendback

    def redirect(self, url):
        self.body_of_the_sendback['redirect'] = url