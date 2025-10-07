import os
from flask import flash, redirect, url_for, Blueprint, render_template
from forms import MessageForm
from message_repository import MessageRepository
from message_service import MessageManager, SteganographyManager

message_bp = Blueprint('messages', __name__)
UPLOAD_FOLDER = 'static/photo'
repo = MessageRepository()
message_service = MessageManager(UPLOAD_FOLDER, repo)
encryption_service = SteganographyManager(UPLOAD_FOLDER, repo)

@message_bp.route('/')
def index():
    all_messages = repo.get_all()
    return render_template('index.html', messages=all_messages)

@message_bp.route('/encrypting', methods=['GET', 'POST'])
def encrypted_message():
    form = MessageForm()
    if form.validate_on_submit():
        try:
            encryption_service.encrypt_message(form.photo.data, form.text.data)
            flash('Message has been encrypted.', 'success')
            return redirect(url_for('messages.index'))
        except Exception as e:
            flash(f'Error while saving message: {str(e)}', 'danger')
    return render_template('encrypted.html', form=form)


@message_bp.route('/view/<int:id>')
def view_photo(id):
    message = repo.get_by_id(id)
    return render_template('view.html', message=message)


@message_bp.route('/delete/<int:id>', methods=['POST'])
def delete_message(id):
    message = repo.get_by_id(id)
    try:
        message_service.delete_message(message)
        flash('Message deleted successfully', 'success')
    except Exception as e:
        flash(f'Error while deleting: {str(e)}', 'danger')
    return redirect(url_for('messages.index'))


@message_bp.route('/decrypting')
def decrypted_message():
    flash('Message has been decrypted.')
    return render_template('decrypted.html')
