import os
from flask import flash, redirect, request, url_for, Blueprint, render_template
from db_config import db
from forms import MessageForm
from models import Message
from werkzeug.utils import secure_filename
message_bp = Blueprint('messages', __name__)
UPLOAD_FOLDER = 'static/photo'
@message_bp.route('/')
def index():
    all_messages = Message.query.order_by(Message.id.desc()).all()
    return render_template('index.html', messages=all_messages)

@message_bp.route('/encrypting', methods=['GET', 'POST'])
def encrypted_message():
    form = MessageForm()
    if form.validate_on_submit():
        photo_file = form.photo.data
        filename = secure_filename(photo_file.filename)
        path = os.path.join(UPLOAD_FOLDER, filename)
        photo_file.save(path)

        new_form = Message(
            text=form.text.data,
            photo=path
        )
        db.session.add(new_form)
        db.session.commit()
        flash('Message has been encrypted.', 'success')
        return redirect(url_for('messages.index'))
    return render_template('encrypted.html', form=form)

@message_bp.route('/view/<int:id>')
def view_photo(id):
    m = Message.query.get_or_404(id)
    return render_template('view.html', message=m)

@message_bp.route('/delete/<int:id>', methods=['POST'])
def delete_message(id):
    message = Message.query.get_or_404(id)
    db.session.delete(message)
    db.session.commit()
    flash('Message deleted successfully', 'success')
    return redirect(url_for('messages.index'))
@message_bp.route('/decrypting')
def decrypted_message():
    flash('Message has been decrypted.')
    return render_template('decrypted.html')



