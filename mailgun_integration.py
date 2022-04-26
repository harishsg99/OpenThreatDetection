import requests

requests.post(
        "https://api.mailgun.net/v3/YOUR_DOMAIN_NAME/messages",
        auth=("api", "YOUR_API_KEY"),
        data={"from": "Excited User <mailgun@YOUR_DOMAIN_NAME>",
              "to": ["bar@example.com", "YOU@YOUR_DOMAIN_NAME"],
              "subject": "Hello",
              "text": "Testing some Mailgun awesomness!"})
