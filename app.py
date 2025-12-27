from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from flask_cors import CORS
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RSVP_FILE = os.path.join(BASE_DIR, 'rsvps.json')

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)
app.secret_key = os.environ.get('WEDDING_SECRET', 'change_this_secret')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')

def load_rsvps():
    if not os.path.exists(RSVP_FILE):
        return []
    with open(RSVP_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except Exception:
            return []

def save_rsvps(data):
    with open(RSVP_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@app.route('/', methods=['GET'])
def index():
    # keep root simple: redirect to the dedicated register page
    return redirect(url_for('register_page'))


@app.route('/register', methods=['GET'])
def register_page():
    # gate page: if session['allowed'] present, redirect to home
    if session.get('allowed'):
        return redirect(url_for('home'))
    return render_template('index.html')

# ...existing code...
# ...existing code...
@app.route('/landing', methods=['GET'])
def landing():
    # página pública que mostra a mesma tela de registro (não altera permissões)
    if session.get('allowed'):
        return redirect(url_for('home'))
    return render_template('index.html')
# ...existing code...

@app.route('/enter', methods=['POST'])
def enter():
    # Expecting name, phone, email, attending
    name = request.form.get('name', '').strip()
    phone = request.form.get('phone', '').strip()
    email = request.form.get('email', '').strip()
    attending = request.form.get('attending', '').strip()

    if not (name and phone and email and attending in ['yes', 'no']):
        return jsonify({'ok': False, 'error': 'Please fill all fields correctly.'}), 400

    rsvps = load_rsvps()
    entry = {'name': name, 'phone': phone, 'email': email, 'attending': attending, 'status': 'pending', 'items': []}
    rsvps.append(entry)
    save_rsvps(rsvps)

    # do not grant access until admin approves
    return jsonify({'ok': True, 'status': 'pending'})


@app.route('/bring', methods=['POST'])
def bring_item():
    # add a contribution item to an RSVP identified by name+email
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    category = request.form.get('category', '').strip() or 'other'
    description = request.form.get('description', '').strip()
    quantity = request.form.get('quantity', '').strip()
    if not (name and email and description):
        return jsonify({'ok': False, 'error': 'Name, email and description required.'}), 400
    rsvps = load_rsvps()
    guest = next((g for g in rsvps if g.get('name') == name and g.get('email') == email), None)
    if not guest:
        return jsonify({'ok': False, 'error': 'RSVP not found.'}), 404
    item = {'category': category, 'description': description, 'quantity': quantity}
    guest_items = guest.get('items') or []
    guest_items.append(item)
    guest['items'] = guest_items
    save_rsvps(rsvps)
    return jsonify({'ok': True, 'item': item})

@app.route('/home')
def home():
    if not session.get('allowed'):
        return redirect(url_for('index'))
    return render_template('home.html')

@app.route('/our-wedding')
def our_wedding():
    if not session.get('allowed'):
        return redirect(url_for('index'))
    name = session.get('guest_name')
    rsvps = load_rsvps()
    guest = next((g for g in rsvps if g.get('name') == name), None)
    if not guest or guest.get('status') != 'approved':
        session.pop('allowed', None)
        session.pop('guest_name', None)
        return redirect(url_for('index'))
    return render_template('our_wedding.html')

@app.route('/our-story')
def our_story():
    if not session.get('allowed'):
        return redirect(url_for('index'))
    name = session.get('guest_name')
    rsvps = load_rsvps()
    guest = next((g for g in rsvps if g.get('name') == name), None)
    if not guest or guest.get('status') != 'approved':
        session.pop('allowed', None)
        session.pop('guest_name', None)
        return redirect(url_for('index'))
    return render_template('our_story.html')

@app.route('/our-rsvp')
def our_rsvp():
    # require session and approved status
    if not session.get('allowed'):
        return redirect(url_for('index'))
    name = session.get('guest_name')
    rsvps = load_rsvps()
    guest = next((g for g in rsvps if g.get('name') == name), None)
    if not guest or guest.get('status') != 'approved':
        # clear session for safety
        session.pop('allowed', None)
        session.pop('guest_name', None)
        return redirect(url_for('index'))
    return render_template('our_rsvp.html', guest=guest)


@app.route('/enter-status', methods=['POST'])
def enter_status():
    name = request.form.get('name', '').strip()
    email = request.form.get('email', '').strip()
    if not (name and email):
        return jsonify({'ok': False, 'error': 'Name and email are required.'}), 400
    rsvps = load_rsvps()
    guest = next((g for g in rsvps if g.get('name') == name and g.get('email') == email), None)
    if not guest:
        return jsonify({'ok': False, 'status': 'not_found'}), 404
    if guest.get('status') == 'approved':
        session['allowed'] = True
        session['guest_name'] = name
        return jsonify({'ok': True, 'status': 'approved'})
    return jsonify({'ok': True, 'status': guest.get('status', 'pending')})


@app.route('/logout')
def logout():
    session.pop('allowed', None)
    session.pop('guest_name', None)
    return redirect(url_for('index'))


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin'))


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        pwd = request.form.get('password', '')
        if pwd == ADMIN_PASSWORD:
            session['admin'] = True
            return redirect(url_for('admin'))
        return render_template('admin_login.html', error='Incorrect password')

    if not session.get('admin'):
        return render_template('admin_login.html')

    rsvps = load_rsvps()
    return render_template('admin.html', rsvps=rsvps)


@app.route('/admin/approve', methods=['POST'])
def admin_approve():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    idx = request.form.get('idx')
    try:
        idx = int(idx)
    except Exception:
        return redirect(url_for('admin'))
    rsvps = load_rsvps()
    if 0 <= idx < len(rsvps):
        rsvps[idx]['status'] = 'approved'
        save_rsvps(rsvps)
    return redirect(url_for('admin'))


@app.route('/admin/reject', methods=['POST'])
def admin_reject():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    idx = request.form.get('idx')
    try:
        idx = int(idx)
    except Exception:
        return redirect(url_for('admin'))
    rsvps = load_rsvps()
    if 0 <= idx < len(rsvps):
        rsvps[idx]['status'] = 'rejected'
        save_rsvps(rsvps)
    return redirect(url_for('admin'))


@app.route('/admin/clear', methods=['POST'])
def admin_clear():
    if not session.get('admin'):
        return redirect(url_for('admin'))
    idx = request.form.get('idx')
    try:
        idx = int(idx)
    except Exception:
        return redirect(url_for('admin'))
    rsvps = load_rsvps()
    if 0 <= idx < len(rsvps):
        # only allow clearing approved or rejected
        if rsvps[idx].get('status') in ('approved', 'rejected'):
            rsvps.pop(idx)
            save_rsvps(rsvps)
    return redirect(url_for('admin'))


@app.route('/gallery')
def gallery():
    # gallery for approved guests only
    if not session.get('allowed'):
        return redirect(url_for('index'))
    images_dir = os.path.join(BASE_DIR, 'static', 'images')
    images = []
    if os.path.exists(images_dir):
        for fname in sorted(os.listdir(images_dir)):
            if fname.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')):
                images.append(url_for('static', filename=f'images/{fname}'))
    return render_template('gallery.html', images=images)

@app.route('/search')
def search():
    # simple search over page names/content
    q = request.args.get('q', '').lower()
    pages = [
        {'path': '/home', 'title': 'Home', 'content': 'Welcome to our wedding'},
        {'path': '/our-wedding', 'title': 'Our Wedding', 'content': 'Event details and venue'},
        {'path': '/our-story', 'title': 'Our Story', 'content': 'How we met'},
        {'path': '/our-rsvp', 'title': 'RSVP', 'content': 'Your RSVP confirmation'}
    ]
    if not q:
        return jsonify(pages)
    matches = [p for p in pages if q in p['title'].lower() or q in p['content'].lower()]
    return jsonify(matches)


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/declare')
def declare_page():
    # require approved session
    if not session.get('allowed'):
        return redirect(url_for('login_page'))
    name = session.get('guest_name')
    rsvps = load_rsvps()
    guest = next((g for g in rsvps if g.get('name') == name), None)
    if not guest or guest.get('status') != 'approved':
        session.pop('allowed', None)
        session.pop('guest_name', None)
        return redirect(url_for('login_page'))
    return render_template('declare.html', guest=guest)

if __name__ == '__main__':
    # ensure rsvps file exists
    if not os.path.exists(RSVP_FILE):
        save_rsvps([])
    app.run(host='0.0.0.0', port=5000, debug=True)
