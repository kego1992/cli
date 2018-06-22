###
The Slack Bot can "listen" to all messages in the room
or "respond" to direct messages (@mybot do this)

More at https://hub.asyncy.com/service/slack-bot
###
slack-bot as bot
    # listens for all messages
    when bot listen to:/foo/i as msg
        bot send text:'bar' room:msg.room

    # reply to direct messages
    when bot respond to:/hello/i as msg
        bot send text:'world' room:msg.room
