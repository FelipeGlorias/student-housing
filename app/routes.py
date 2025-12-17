from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app import db
from app.models import Listing, Booking, Review
from app.forms import ListingForm, BookingForm, ReviewForm, SearchForm
from datetime import datetime

main = Blueprint('main', __name__)

@main.route('/')
def index():
    search_form = SearchForm()
    listings = Listing.query.filter_by(is_active=True).order_by(Listing.created_at.desc()).limit(6).all()
    return render_template('index.html', listings=listings, search_form=search_form)

@main.route('/listings')
def listings():
    search_form = SearchForm()
    query = Listing.query.filter_by(is_active=True)
    if request.args.get('search'):
        term = request.args.get('search')
        query = query.filter((Listing.title.contains(term)) | (Listing.description.contains(term)))
    if request.args.get('min_price'):
        query = query.filter(Listing.price_per_month >= float(request.args.get('min_price')))
    if request.args.get('max_price'):
        query = query.filter(Listing.price_per_month <= float(request.args.get('max_price')))
    if request.args.get('bedrooms'):
        query = query.filter(Listing.bedrooms >= int(request.args.get('bedrooms')))
    all_listings = query.order_by(Listing.created_at.desc()).all()
    return render_template('listings.html', listings=all_listings, search_form=search_form)

@main.route('/listing/<int:listing_id>')
def listing_detail(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    reviews = Review.query.filter_by(listing_id=listing_id).order_by(Review.created_at.desc()).all()
    avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
    booking_form = BookingForm() if current_user.is_authenticated else None
    review_form = ReviewForm() if current_user.is_authenticated else None
    return render_template('listing_detail.html', listing=listing, reviews=reviews, avg_rating=avg_rating,
                           booking_form=booking_form, review_form=review_form)

@main.route('/listing/create', methods=['GET', 'POST'])
@login_required
def create_listing():
    form = ListingForm()
    if form.validate_on_submit():
        listing = Listing(
            title=form.title.data,
            description=form.description.data,
            address=form.address.data,
            city=form.city.data,
            state=form.state.data,
            zip_code=form.zip_code.data,
            price_per_month=form.price_per_month.data,
            bedrooms=form.bedrooms.data,
            bathrooms=form.bathrooms.data,
            square_feet=form.square_feet.data,
            available_from=form.available_from.data,
            available_to=form.available_to.data,
            amenities=form.amenities.data,
            owner_id=current_user.id
        )
        try:
            db.session.add(listing)
            db.session.commit()
            flash('Listing created successfully!', 'success')
            return redirect(url_for('main.listing_detail', listing_id=listing.id))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('create_listing.html', form=form)

@main.route('/listing/<int:listing_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.owner_id != current_user.id:
        abort(403)
    form = ListingForm(obj=listing)
    if form.validate_on_submit():
        listing.title = form.title.data
        listing.description = form.description.data
        listing.address = form.address.data
        listing.city = form.city.data
        listing.state = form.state.data
        listing.zip_code = form.zip_code.data
        listing.price_per_month = form.price_per_month.data
        listing.bedrooms = form.bedrooms.data
        listing.bathrooms = form.bathrooms.data
        listing.square_feet = form.square_feet.data
        listing.available_from = form.available_from.data
        listing.available_to = form.available_to.data
        listing.amenities = form.amenities.data
        listing.updated_at = datetime.utcnow()
        try:
            db.session.commit()
            flash('Listing updated successfully!', 'success')
            return redirect(url_for('main.listing_detail', listing_id=listing.id))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return render_template('edit_listing.html', form=form, listing=listing)

@main.route('/listing/<int:listing_id>/delete', methods=['POST'])
@login_required
def delete_listing(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    if listing.owner_id != current_user.id:
        abort(403)
    try:
        db.session.delete(listing)
        db.session.commit()
        flash('Listing deleted successfully!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('main.dashboard'))

@main.route('/listing/<int:listing_id>/book', methods=['POST'])
@login_required
def create_booking(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = BookingForm()
    if form.validate_on_submit():
        days = (form.end_date.data - form.start_date.data).days
        months = max(days / 30, 0.5)
        total_price = listing.price_per_month * months
        booking = Booking(
            listing_id=listing_id,
            tenant_id=current_user.id,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            total_price=total_price,
            message=form.message.data
        )
        try:
            db.session.add(booking)
            db.session.commit()
            flash('Booking request sent successfully!', 'success')
            return redirect(url_for('main.dashboard'))
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('main.listing_detail', listing_id=listing_id))

@main.route('/booking/<int:booking_id>/update/<string:status>', methods=['POST'])
@login_required
def update_booking(booking_id, status):
    booking = Booking.query.get_or_404(booking_id)
    listing = Listing.query.get(booking.listing_id)
    if status == 'confirmed' and listing.owner_id != current_user.id:
        abort(403)
    if status == 'cancelled' and booking.tenant_id != current_user.id and listing.owner_id != current_user.id:
        abort(403)
    booking.status = status
    booking.updated_at = datetime.utcnow()
    try:
        db.session.commit()
        flash(f'Booking {status} successfully!', 'success')
    except:
        db.session.rollback()
        flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('main.dashboard'))

@main.route('/listing/<int:listing_id>/review', methods=['POST'])
@login_required
def create_review(listing_id):
    listing = Listing.query.get_or_404(listing_id)
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            listing_id=listing_id,
            reviewer_id=current_user.id,
            rating=form.rating.data,
            comment=form.comment.data,
            review_type='listing'
        )
        try:
            db.session.add(review)
            db.session.commit()
            flash('Review posted successfully!', 'success')
        except:
            db.session.rollback()
            flash('An error occurred. Please try again.', 'danger')
    return redirect(url_for('main.listing_detail', listing_id=listing_id))

@main.route('/dashboard')
@login_required
def dashboard():
    my_listings = Listing.query.filter_by(owner_id=current_user.id).all()
    listing_ids = [l.id for l in my_listings]
    received_bookings = Booking.query.filter(Booking.listing_id.in_(listing_ids)).all() if listing_ids else []
    my_bookings = Booking.query.filter_by(tenant_id=current_user.id).all()
    return render_template('dashboard.html', my_listings=my_listings, received_bookings=received_bookings, my_bookings=my_bookings)

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contact')
def contact():
    return render_template('contact.html')
