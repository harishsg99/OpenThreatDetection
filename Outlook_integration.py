from O365 import Account

credentials = ('client_id', 'client_secret')

account = Account(credentials)
m = account.new_message()
m.to.add('to_example@example.com')
m.subject = 'Testing!'
m.body = "George Best quote: I've stopped drinking, but only while I'm asleep."
m.send()
