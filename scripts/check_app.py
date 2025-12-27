from app import app

paths = ['/', '/register', '/login', '/admin', '/our-wedding', '/our-story', '/our-rsvp']
with app.test_client() as c:
    for p in paths:
        rv = c.get(p)
        print(p, rv.status_code)
        if rv.status_code in (200,302):
            data = rv.get_data(as_text=True)
            print(data[:180].replace('\n', ' '))
        print('---')
