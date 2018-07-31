###
Serverless request handler

More at https://hub.asyncy.com/service/http
###

when http listen method:'get' path:'/' as client
    client write message:'Hello world!'
