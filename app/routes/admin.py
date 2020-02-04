from app import app


@app.route('/admin', methods=['GET', 'POST'])
def admin_index():
    return 'Hello Admin!'
