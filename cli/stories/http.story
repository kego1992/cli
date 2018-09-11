###
Serverless request handler

More at https://hub.asyncy.com/service/http
###

http server as client
    when client listen method:'get' path:'/' as request
        request write content:'Hello world!'
