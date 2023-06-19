@main_bp.route('/send_email', methods=['POST'])
@login_required
def send_email():
    history_id = request.form.get('history_id')
    # ... fetch the search result based on history_id ...
    # ... construct the email message with the search result ...
    # ... send the email using Flask-Mail ...

    flash('Email sent successfully!', 'success')
    return redirect(url_for('main.search_history'))