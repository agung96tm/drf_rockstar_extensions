Fetcher Field
====================

This field used to fetch data from api's


.. code-block:: python

   class UserSerializer(serializer.SerializerModel):
       ## PARAMS
       ## (GET: query_params, POST,PUT,PATCH,DELETE: body_params
       todos = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/todos',
          fetch_action='get' # default: 'get'
          params={
              'userId': 'id',
          }
       )
       # translate: https://jsonplaceholder.typicode.com/todos?userId=<id>

       ## PATH PARAMS
       extra_info = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/{path_user}/{id}',
          path_params={
              # 👇 use `users` instead of value from user instance
              'path_user': 'users',
              'id': 'id',
          }
       )
       # translate: https://jsonplaceholder.typicode.com/users/<id>

       ## TARGET_SOURCE
       # url: `http://localhost/users/<id>/musics`
       # response:
       # {
       #   "data": [
       #        {id: 1, name: 'Hip Hop'},
       #        {id: 2, name: 'Rock'},
       #   ]
       # }
       # we want get musics from 'data' key, so we define 'target_source'
       musics = FetcherField(
          fetch_url='http://localhost/users/{id}/musics',
          path_params={
              'id': 'id',
              # 👇 support nested source, define like 'data.extras'
              'target_source': 'data',
          }
       )

       class Meta:
          model = User
          fields = ('id', 'username', 'todos',)
