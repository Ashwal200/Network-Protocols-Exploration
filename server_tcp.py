from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.request

class ImageHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = None
        data = self.path
        word_list = data.split("/")
        type = word_list[1]
        protocol = word_list[2]
        

        if type == "cat":
            url = 'https://upload.wikimedia.org/wikipedia/commons/a/a5/Red_Kitten_01.jpg'
            content_type = "image/jpeg"
        elif type == "dog":
            url = 'https://upload.wikimedia.org/wikipedia/commons/9/94/My_dog.jpg'
            content_type = "image/jpeg"
        elif type == "video":
            url = 'https://www.youtube.com/watch?v=4rhpbCcSXVs'
            content_type = "video/mp4"
        elif type == "amit":
            url = 'https://scontent.fsdv2-1.fna.fbcdn.net/v/t39.30808-6/337403624_625560219387248_6776912049187129348_n.jpg?stp=cp6_dst-jpg_s1080x2048&_nc_cat=106&ccb=1-7&_nc_sid=730e14&_nc_ohc=pKIbnxA08i8AX-dg44t&_nc_ht=scontent.fsdv2-1.fna&oh=00_AfCtWnMUP7cZ4mPd6zAMADKlygwiLdxUrWUSTySxqDp7xg&oe=64210FC4'
            content_type = "image/jpeg"
        else:
            url = 'http://www.amitdvir.com/'
            content_type = "text/html"

        with urllib.request.urlopen(url) as f:
            data_file = f.read()

        self.send_response(200)
        self.send_header("Content-type", content_type)
        self.end_headers()
        self.wfile.write(data_file)


if __name__ == "__main__":
    server_address = ('localhost', 20139)
    httpd = HTTPServer(server_address, ImageHandler)
    print("The tcp server started on port 20139...")
    httpd.serve_forever()
