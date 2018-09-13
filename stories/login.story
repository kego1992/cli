http server as client
    when client listen path:'/github' as request
        state = request.arguments['state']  # cli generated
        request redirect url:'https://github.com/login/oauth/authorize?state={state}'

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

        res = graphql exec
            query:'mutation($data:CreateOwnerByLoginInput!){createOwnerByLogin(input:$data){uuid}}'
            data:{
              'data': {
                'service': 'GITHUB',
                'serviceId': user.service_id,
                'username': user.login,
                'name': user.name,
                'email': user.email,
                'oauthToken': token.data['access_token']
              }
            }

        redis rpush key:state value:{
            'id': res['data']['createownerbylogin']['json']['owner_uuid'],
            'access_token': res['data']['createownerbylogin']['json']['token_uuid'],
            'name': user.name,
            'email': user.email,
            'username': user.login
        }

    when client listen path:'/oauth_callback' as request
        user_data = redis brpop key:request.arguments['state']  # cli generated uuid
        request write content:user_data
        request finish
