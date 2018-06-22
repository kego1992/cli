###
Handle websocket clients

More at https://hub.asyncy.com/service/websocket
###

websocket path:'/ws' as ws
    when ws open as event
        # ...

    when ws message as event
        # ...

    when ws close as event
        # ...
