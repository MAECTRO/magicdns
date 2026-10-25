import urllib.request

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        print('REDIRECT TO:', newurl)
        return None

opener = urllib.request.build_opener(NoRedirect)
try:
    opener.open('https://vertexaisearch.cloud.google.com/grounding-api-redirect/AUZIYQFds20jWuqpOrraT_QJyOAjvlUkyZ0tizvVMev-GAjFG2JbQEDjy3KaHkTJvOq03pci36cRus9umEoX_5l85pLS1dp5ZLuXEx1lZ4Q8O3k8pQLeOXb4Sq6J9cQJ6BwdtzG-OWELnx-j_4-7ToY1mnA=')
except Exception as e:
    pass
