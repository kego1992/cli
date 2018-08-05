###
The Slack Bot can "listen" to all messages in the room
or "respond" to direct messages (@mybot do this)

More at https://hub.asyncy.com/service/slack
###
slack bot as client
    # listens for all messages
    when client hears pattern:/foo/i as msg
        msg reply text:'bar' room:msg.room

    # reply to direct messages
    when client responds pattern:/hello/i as msg
        msg reply text:'world' room:msg.room
