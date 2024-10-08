import http.server
import random
import io

from prometheus_client import Counter, exposition

COUNTER_NAME = 'akash_requests_count'
REQUESTS_COUNT = Counter(COUNTER_NAME, 'Count', ['endpoint'])


class RequestsHandler(exposition.MetricsHandler):

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length)  # Read the data
        print("POST request")
        print(post_data.decode('utf-8'))  # Decode the data to a string
        self.send_response(500)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write('POST request received'.encode())

    def do_GET(self):
        if self.path not in ('/foo', '/bar', '/metrics'):
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write('404: Not found'.encode())
            return

        if self.path in ('/foo', '/bar'):
            REQUESTS_COUNT.labels(endpoint=self.path).inc()
            current_count = self._get_current_count()
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(
                f'Current count: [{self.path}] {current_count}'.encode())
        else:
            return super().do_GET()

    def _get_current_count(self):
        sample = [s for s in REQUESTS_COUNT.collect()[0].samples
                  if s.name == f'{COUNTER_NAME}_total' and
                  s.labels['endpoint'] == self.path][0]
        return sample.value


if __name__ == '__main__':
    cpu = "a" * random.randint(1, 5) * 1000000
    for path in ('/foo', '/bar'):
        REQUESTS_COUNT.labels(endpoint=path)

    server_address = ('', 8080)
    httpd = http.server.HTTPServer(server_address, RequestsHandler)
    print('Server started')
    httpd.serve_forever()
