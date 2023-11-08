
import requests

with open('sample.pdf', 'r') as f:
    file_content = f.read()
    files = {
        'files': ('sample.pdf', file_content)
    }
    data = {
        'email': 'tejas@mail.com'
    }
    result = requests.post(
        f'https://c1e0-34-34-36-126.ngrok-free.app/uploadfiles', files=files, data=data, headers={

        })

    print(result.json())
