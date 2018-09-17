http server as client
    when client listen path:'/github' as request
        state = request.arguments['state']  # cli generated
        scope = request.arguments['scope']
        request redirect url:'https://github.com/login/oauth/authorize'
                         query:{
                            'state': state,
                            'scope': scope,
                            'client_id': app.secrets.github_client_id,
                            'redirect_uri': 'https://login.asyncy.com/github/oauth_success'
                         }

    # Postback URL for the GH oauth, initiated via the CLI
    # The URL should look something like this - https://login.asyncy.com/oauth_success
    when client listen path:'/github/oauth_success' as request
        state = request.arguments['state']  # cli generated
        code = request.arguments['code']  # gh auth code
        body = {
            'client_id': app.secrets.github_client_id,
            'client_secret': app.secrets.github_client_secret,
            'code': code,
            'state': state
        }
        token = http fetch path:'https://github.com/login/oauth/access_token'
                           method:'post' :body

        # https://developer.github.com/v3/users/#get-the-authenticated-user
        user = github api endpoint:'/user' token:token.data['access_token']

        res = psql exec
          query:'select create_owner_by_login({service}, {service_id}, {username}, {name}, {email}, {oauth_token}) as data;'
          data:{
            'service': 'GITHUB',
            'service_id': user.service_id,
            'username': user.login,
            'name': user.name,
            'email': user.email,
            'oauth_token': token.data['access_token']
          }

        redis rpush key:state value:{
            'id': res[0]['data']['owner_uuid'],
            'access_token': res[0]['data']['token_uuid'],
            'name': user.name,
            'email': user.email,
            'username': user.login
        }

    when client listen path:'/oauth_callback' as request
        user_data = redis brpop key:request.arguments['state']  # cli generated uuid
        request write content:user_data
        request finish
