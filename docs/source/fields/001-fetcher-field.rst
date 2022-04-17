Fetcher Field
====================

A field that help you fetching a data from API with easy implementation.

-------
Usage
-------
.. code-block:: python

   class UserSerializer(serializers.ModelSerializer):
      profile = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/users/{userId}',
          fetch_action='get' # optional, default is 'get'
          path_params={ # 👈 userId from url replaced with id from user instance
              'userId': 'id',
          }
      )

      class Meta:
        model = User  # User <id: 1>
        fields = ('id', 'name', 'profile')


From an example above we want to fetching data from jsonplaceholder api.
We fetch a user with `get` action,
and using id from current user instance to replace `user_id`
(https://jsonplaceholder.typicode.com/users/1).


Fetcher Field **support list** too.

.. code-block:: python

   class UserSerializer(serializers.ModelSerializer):
      todos = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/todos/',
          params={
            'userId': 'id', # 👈 send as query_params
          }
      )

      class Meta:
        model = User  # User <id: 1>
        fields = ('id', 'name', 'todos')

-------
Action
-------

Image you need fetching an data from `POST` action, we can specific an action using `fetch_action` argument.

.. code-block:: python

   class UserSerializer(serializers.ModelSerializer):
      profile = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/users/',
          fetch_action='post' # 👈 post,get,put,patch,etc. default is get
          params={
              'user_id': 'id', # 👈 send as body requests
          }
      )

      class Meta:
        model = User  # User <id: 1>
        fields = ('id', 'name', 'profile')

--------------
Target Source
--------------
We will talk about json data with example bellow:

.. code-block::

   // url: https://www.example.com/users/1
   {
      "user": {
          "id": 1,
          "full_name": "Agung Yuliyanto",
      }
   }

How to get data inside user key? easy, using `target_source` argument.

.. code-block:: python

   class UserSerializer(serializers.ModelSerializer):
      profile = FetcherField(
          fetch_url='https://www.example.com/users/{userId}',
          path_params={
            'userId': 'id',
          },
          target_source='user', # 👈 nested supported, use '.' (ex: 'data.user')
      )

      class Meta:
        model = User  # User <id: 1>
        fields = ('id', 'name', 'profile')



----------------
Response Source
----------------
When we should using `response source`? When data that we need in a key (ex: 'data') after process `target source`.

.. code-block::

   // url: https://www.example.com/users/1
   {
      "todos": [
        {
          "data": {
             "id": 1,
             "full_name": "Go Work",
          }
        },
        {
          "data": {
             "id": 1,
             "full_name": "Go Work",
          }
        }
      ]
   }

.. code-block:: python

   class UserSerializer(serializers.ModelSerializer):
      profile = FetcherField(
          fetch_url='https://www.example.com/todos',
          params={
            'userId': 'id',
          },
          target_source='todos',
          response_source='data',  # 👈 nested supported, use '.' (ex: 'data.user')
          response_source_in_list=True,
      )

      class Meta:
        model = User  # User <id: 1>
        fields = ('id', 'name', 'todos')


----------------
Serializer
----------------
Fetcher Field support using serializer.
So data can more specific instead of showing all response data.

.. code-block:: python

   class ProfileSerializer(serializer.Serializer):
       email = serializer.EmailField()
       phone = serializer.CharField()
       website = serializer.CharField()

   class UserSerializer(serializer.SerializerModel):
       profile = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/users/{userId}',
          path_params={
              'userId': 'id',
          },
          serializer=ProfileSerializer # 👈 here
       )

       class Meta:
          model = User
          fields = ('id', 'name', 'profile',)


How about list data? Dont worry fetcher field support it.

.. code-block:: python

   class TodoSerializer(serializer.Serializer):
       id = serializer.IntegerField()
       title = serializer.CharField()
       completed = serializer.BooleanField()

   class UserSerializer(serializer.SerializerModel):
       todos = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/todos',
          params={  # pass as query_params
              'userId': 'id',
          },
          serializer=TodoSerializer # 👈 here, auto detect looking by response
       )

       class Meta:
          model = User
          fields = ('id', 'name', 'todos',)


----------------
Authentication
----------------
Fetcher field support to handle authentication.

.. code-block:: python

   def my_basic_auth(field, obj, request, **kwargs):
     user = request.user
     auth = {}
     if user is not None and user.is_authenticated:
         auth = {
            'auth': (
                user.basic_username,
                user.basic_password,
            )
         }
     return auth

   class UserSerializer(serializer.SerializerModel):
       profile = FetcherField(
          fetch_url='https://jsonplaceholder.typicode.com/users/{userId}',
          path_params={
            'userId': 'id',
          },
          auth=my_basic_auth
       )

       class Meta:
          model = User
          fields = ('id', 'name', 'profile',)


by default fetcher field using function has defined in `settings.py`.

.. code-block:: python

   DRF_ROCKSTAR = {
      # define custom authentication
      'DEFAULT_FETCHER_FIELD_AUTH': 'myapps.serializers.my_basic_auth'
   }