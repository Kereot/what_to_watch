from random import randrange

from flask import abort, render_template, flash, redirect, url_for

from . import app, db
from .dropbox import async_upload_files_to_dropbox, upload_files_to_dropbox
from .forms import OpinionForm
from .models import Opinion


def random_opinion():
    quantity = Opinion.query.count()
    if quantity:
        offset_value = randrange(quantity)
        opinion = Opinion.query.offset(offset_value).first()
        return opinion
    return None

@app.route('/')
def index_view():
    opinion = random_opinion()
    if opinion is None:
        abort(500)
    return render_template('opinion.html', opinion=opinion)


@app.route('/add', methods=('GET', 'POST'))
async def add_opinion_view():
    form = OpinionForm()
    if form.validate_on_submit():
        text = form.text.data
        if Opinion.query.filter_by(text=text).first() is not None:
            flash('Такое мнение уже было оставлено ранее!', 'duplicate')
            return render_template('add_opinion.html', form=form)
        urls = await async_upload_files_to_dropbox(form.images.data)
        opinion = Opinion(
            title=form.title.data,
            text=form.text.data,
            source=form.source.data,
            images=urls
        )
        db.session.add(opinion)
        db.session.commit()
        return redirect(url_for('opinion_view', id=opinion.id))
    return render_template('add_opinion.html', form=form)


@app.route('/opinions/<int:id>')
def opinion_view(id):
    opinion = Opinion.query.get_or_404(id)
    return render_template('opinion.html', opinion=opinion)
