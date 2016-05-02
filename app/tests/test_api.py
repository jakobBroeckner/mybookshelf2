from .basecase import TestCase
from urllib.parse import quote
import flask

class TestApi(TestCase):
    def __init__(self, *args, **kwargs):
        super(TestApi, self).__init__(*args, **kwargs)
        self.headers=None
    def login(self, user='admin', pwd='admin'):
        res=self.client.post('/login', data='{"username":"%s", "password":"%s"}'%(user,pwd), 
                           content_type='application/json')
        token=res.json.get('access_token')
        self.assertTrue(token)
        self.headers={'Authorization': 'Bearer %s'%token}
    
    def __getattr__(self, name):  
        name=name.upper()
        if name in ('GET', 'POST', 'DELETE', 'PUT', 'OPTIONS'):
            def req(*args, **kwargs):
                kwargs['method']=name
                if 'headers' in kwargs:
                    kwargs['headers'].update(self.headers)
                else:
                    kwargs['headers']=self.headers
                failure=kwargs.pop('failure') if 'failure' in kwargs else False  
                resp= self.client.open(*args,**kwargs) 
                if not failure:
                    self.assert200(resp)
                    return resp.json
                return resp
            return req
        raise AttributeError('Attribute %s not found'%name)                    
    
    def test_api(self):
        res=self.get('/api/ebooks', failure=True)
        self.assert401(res)
        self.login()
        res=self.get('/api/ebooks')
        
        self.assertTrue(len(res['items'])>5)
        self.assertEqual(res['page'], 1)
        self.assertTrue(flask.g.authenticated)
        self.assertEqual(flask.g.user.user_name, 'admin')
        
        for b in res['items']:
            self.assertTrue(b['title'] and b['id'], 'Invalid ebook %s'%b)
            
        res=self.get('/api/ebooks', query_string={'page':1, 'page_size':12, 'sort':'title'})
        self.assertEqual(res['page'], 1)
        self.assertEqual(res['total'], 100)
        self.assertEqual(res['page_size'], 12)
        self.assertEqual(len(res['items']), 12)
        self.assertEqual(res['items'][0]['title'], 'Alenka v říši kvant - Alegorie kvantové fyziky')
        
        first_book=res['items'][0]
        
        res=self.get('/api/ebooks', query_string={'page':9, 'page_size':12, 'sort':'-title'})
        self.assertEqual(res['page'], 9)
        self.assertEqual(len(res['items']), 4)
        self.assertEqual(res['total'], 100)
        self.assertEqual(res['page_size'], 12)
        self.assertEqual(res['items'][-1]['title'], 'Alenka v říši kvant - Alegorie kvantové fyziky')
        last_book=res['items'][-1]
        
        self.assertEqual(first_book, last_book)
        
        
        res=self.get('/api/ebooks', query_string={'page':9, 'page_size':12, 'sort':'blba'}, failure=True)
        self.assert400(res)
        
        res=self.get('/api/ebooks', query_string={'page':0, 'page_size':12, 'sort':'-title'}, failure=True)
        self.assert400(res)
        
        res=self.get('/api/ebooks', query_string={'page':1, 'page_size':-1, 'sort':'-title'},  failure=True)
        self.assert400(res)
        
        res=self.get('/api/ebooks', query_string={'page':1, 'page_size':101, 'sort':'-title'},  failure=True)
        self.assert400(res)
        
        res=self.get('/api/ebooks', query_string={'page':10, 'page_size':12, 'sort':'title'},  failure=True)
        self.assert404(res)
        
        id=first_book['id']
        
        res=self.get('/api/ebooks/%s'%id)
        self.assertEqual(res['id'],id)
        self.assertEqual(res['title'], 'Alenka v říši kvant - Alegorie kvantové fyziky')
        
        
        #------------
        res=self.get('/api/authors', query_string={'page':1, 'page_size':50, 'sort':'name'})
        self.assertEqual(len(res['items']),50)
        self.assertEqual(res['total'], 102)
        self.assertEqual(res['items'][0]['last_name'], 'Adornetto')
        
        res=self.get('/api/series', query_string={'page':2, 'page_size':14, 'sort':'title'} )
        self.assertEqual(res['total'], 28)
        self.assertEqual(res['items'][-1]['title'], 'Zář')
        
        
        res=self.get('/api/search/%s'% quote('Zápas boh'))
        self.assertEqual(res['total'], 1)
        self.assertEqual(res['items'][0]['title'], 'Podobni bohům')
        
        res=self.get('/api/search/%s'% quote('prip'))
        self.assertEqual(res['total'], 4)
        
        res=self.get('/api/search/%s'% quote('henry dome'))
        self.assertEqual(res['total'], 1)
        self.assertEqual(res['items'][0]['title'], 'Roky v Bílém domě')
        
        
        
        
        
        
        
        
        
        
        
        