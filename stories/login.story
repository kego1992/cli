http server as client
    when client listen path: '/github' as request
        state = request.query_params['state']  # cli generated
        redirect_url = 'https://login.asyncyapp.com/github/oauth_success'
        request redirect url: 'https://github.com/login/oauth/authorize' query: {'scope': 'user:email', 'state': state, 'client_id': app.secrets.github_client_id, 'redirect_uri': redirect_url}

    # Postback URL for the GH oauth, initiated via the CLI
    # The URL should look something like this - https://login.asyncyapp.com/github/oauth_success
    when client listen path:'/github/oauth_success' as request
        state = request.query_params['state']  # cli generated
        code = request.query_params['code']  # gh auth code

        # Get the oauth_token.
        body = {'client_id': app.secrets.github_client_id, 'client_secret': app.secrets.github_client_secret, 'code': code, 'state': state}
        headers = {'Content-Type': 'application/json; charset=utf-8', 'Accept': 'application/json'}
        gh_response = http fetch url: 'https://github.com/login/oauth/access_token' method: 'post' body: body headers: headers
        token = gh_response['access_token']

        headers = {'Authorization': 'bearer {token}'}
        user = http fetch url: 'https://api.github.com/user' headers: headers

        # Insert into postgres.
        service_id = user['id']
        creds_raw = psql exec query: 'select create_owner_by_login(%(service)s, %(service_id)s, %(username)s, %(name)s, %(email)s, %(oauth_token)s) as data' data: {'service': 'github', 'service_id': '{service_id}', 'username': user['login'], 'name': user['name'], 'email': user['email'], 'oauth_token': token}
        creds = creds_raw['results'][0]['data']

        # Get the token secret.
        secret_raw = psql exec query: 'select secret from token_secrets where token_uuid=%(token_uuid)s' data: {'token_uuid': creds['token_uuid']}
        token_secret = secret_raw['results'][0]['secret']

        # Push the state in Redis.
        redis set key: state value: (json stringify content: {'id': creds['owner_uuid'], 'access_token': token_secret, 'name': user['name'], 'email': user['email'], 'username': user['login']})
        redis expire key: state seconds: 3600  # One hour.
        request set_header key: 'Content-Type' value: 'text/html; charset=utf-8'
        request write content: '<!DOCTYPE html> <html> <head>  <meta charset="UTF-8">  <title>Asyncy</title> </head> <body> <div style="width: 416px; margin: 0 auto;">  <h1 style="text-align: center;">Logged in!</h1>  <br>  <span style="text-align: center; display: block;">Head back to your terminal. The future awaits.<br>Cheers 🍻!</span>  <br>  <img src="https://judepereira.com/nocache/bot.svg" height=500/> </div> </body> </html> '

    # The Asyncy CLI will long poll this endpoint to get login creds.
    when client listen path:'/github/oauth_callback' as request
        user_data = redis get key: request.query_params['state']  # CLI generated uuid.
        request set_header key: 'Content-Type' value: 'application/json; charset=utf-8'
        request write content: user_data['result']
        request finish

