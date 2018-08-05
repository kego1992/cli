###
subscribe is a service that is a handler for
events posted by applications

  # Node via `npm install asyncy`
  # Ruby via `gem install asyncy`

  # Python via `pip install asyncy`
  from asyncy import Asyncy
  asyncy = Asyncy('API_KEY')
  res = asyncy.runSync('foobar', {'hello': 'world'})
  res = await asyncy.runAsync('foobar', {'hello': 'world'})

More at https://hub.asyncy.com/service/subscribe
###

when events triggered name:'foobar' as event
    log event.data

every seconds:3
    events publish name:'foobar' data:'hello world'
