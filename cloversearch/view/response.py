from django.http import HttpResponse
import json


class Response:
    encoder = None

    def __init__(self, data=''):
        self.encoder = None
        self.output = {
            'status': '',
            'msg': ''
        }
        if len(data) > 0:
            self.output['data'] = data

    def error(self, error_type: str, error_msg='', status_code=200):
        """根据提供错误信息响应"""
        self.output['status'] = 'error'
        self.output['error_type'] = error_type
        self.output['msg'] = error_msg
        content = json.dumps(self.output, ensure_ascii=False, cls=self.encoder)
        response = HttpResponse(content, content_type='application/json; charset=utf-8', status=status_code)
        return response

    def exception(self, exception: object, msg='', status_code=200) -> HttpResponse:
        """根据异常响应"""
        self.output['status'] = 'error'
        self.output['exception'] = exception.__str__()
        self.output['error_type'] = type(exception).__name__
        self.output['repr'] = repr(exception)
        self.output['msg'] = msg
        content = json.dumps(self.output, ensure_ascii=False, cls=self.encoder)
        response = HttpResponse(content, content_type='application/json; charset=utf-8', status=status_code)
        return response

    def ok(self, msg='no message', status_code=200) -> HttpResponse:
        self.output['status'] = 'ok'
        self.output['msg'] = msg
        content = json.dumps(self.output, ensure_ascii=False, cls=self.encoder)
        response = HttpResponse(content, content_type='application/json; charset=utf-8', status=status_code)
        return response

    def __getitem__(self, item):
        return self.output[item]

    def __setitem__(self, key, value):
        self.output[key] = value
