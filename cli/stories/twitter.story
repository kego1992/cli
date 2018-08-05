###
Every time someone tweets `#asyncy` like it.

More at https://hub.asyncy.com/service/twitter
###

twitter stream as tw
    when tw tweets hashtag:'asyncy' as tweet
        tweet like
        tweet retweet
