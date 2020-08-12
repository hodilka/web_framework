import pathlib


class Route:
    
    @staticmethod
    def view(html_file):
        PUBLIC_DIR = str(pathlib.Path(__file__).parent.absolute()) + '/static/views/'
        file = open(PUBLIC_DIR + html_file, mode='r')

        # read all lines at once
        html_view = file.read()
        
        # close the file
        file.close()
        return html_view