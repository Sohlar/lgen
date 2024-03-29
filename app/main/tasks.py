from app.extensions import db, celery

# from app.services.search_engines import GoogleSearch

from app.main.models import SearchResult, ContactInfo, Email, Phone, User
from flask_mail import Message
from app import celery, mail
from app.services.logger import logger
from app.services.search_3 import GoogleSearch
import stripe
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from flask import current_app, url_for, render_template

@celery.task(bind=True, name="main.search_engine_task")
def search_engine_task(self, search_history_id, query, cost, user_id):
    logger.debug("Entering celery task\n\n")

    # results = SearchEngineFactory.create_search_engine(engine=engine_str).search(query=query, num_urls = cost)

    gs = GoogleSearch()

    results = list(gs.search(query, num_urls=cost))

    logger.debug("Search ended *\ Adding Results to DB\n")

    try:
        all_emails = []
        all_phones = []
        all_urls = []

        for result in results:
            if result["email"] or result["phone"]:
                emails = result["email"]
                phones = result["phone"]
                urls = result["url"]

                all_emails.extend(emails)
                all_phones.extend(phones)
                all_urls.append(urls)

                search_result = SearchResult(
                    search_history_id=search_history_id, url=result["url"]
                )
                logger.debug(f"*Search Result:\n {search_result}")
                db.session.add(search_result)
                db.session.flush()  # Flush the session to get the id of search_result

                contact_info = ContactInfo(search_result_id=search_result.id)
                logger.debug(f"*Contact Info:\n {contact_info}")
                db.session.add(contact_info)
                db.session.flush()  # Flush the session to get the id of contact_info

                for email_addr in emails:
                    email = Email(contact_info_id=contact_info.id, email=email_addr)
                    logger.debug(f"*/ Email Added: {email}")
                    db.session.add(email)
                    db.session.flush()  # Flush the session to get the id of email
                logger.debug("Emails added")

                for phone_addr in phones:
                    phone = Phone(contact_info_id=contact_info.id, phone=phone_addr)
                    logger.debug(f"*/ Phone Added: {phone}")
                    db.session.add(phone)
                    db.session.flush()  # Flush the session to get the id of phone
                logger.debug("Phones added")

        db.session.commit()
        logger.debug("_---------------")
        logger.debug("Search and Record Finished")
        logger.debug("_---------------")
        logger.debug("_---------------")
        logger.debug("Initializing email")
        logger.debug("_---------------")



        # Send result emails after the search is complete
        user = User.query.get(user_id)
        logger.debug(f"*/--------\n*/------{user}\n*/--------")

        send_email_async(
            {"emails": all_emails, "phones": all_phones, "urls": all_urls}, user.email
        )

    except Exception as e:
        db.session.rollback()
        logger.exception("An error Occurred, transaction rolled back", e)

    finally:
        # Explicitly remove the session to avoid memory leaks
        db.session.remove()


""" def get_most_recent_search_result(user_id, search_history_id):
    search_history = SearchHistory.query.get(user_id).first()

    if not search_history:
        print("No search history found for the given id and user.")
        return
    
    most_recent_search_result = search_history.results.order_by(SearchResult.id.desc()).first()

    if most_recent_search_result:
        return most_recent_search_result
        
    else:
        print("No search results found for the given search history.")
        return """


def get_most_recent_search_result(user):
    # Retrieve the user instance by user_id

    if not user:
        print("No user found for the given id.")
        return

    # Get the search history for the user
    search_history = user.search_history
    logger.debug(f"{search_history}")
    logger.debug(type(search_history))

    if not search_history:
        print("No search history found for the given user.")
        return

    # Get the most recent search result from the user's search history
    most_recent_search_result = search_history.results.order_by(
        SearchResult.id.desc()
    ).first()

    if most_recent_search_result:
        return most_recent_search_result
    else:
        print("No search results found for the given search history.")
        return


@celery.task(bind=True)
def process_purchase(self, user_id, num_tokens, stripe_token):
    user = User.query.get(user_id)
    stripe.api_key = 'your-secret-key'

    try:
        # Create a stripe charge for the token purchase
        charge = stripe.Charge.create(
            amount=num_tokens * 110,
            currency="usd",
            source=stripe_token,
            description=f"Token purchase for {user.username}",
        )

        # Check if the charge was successful
        if charge['paid']:
            # Update user's token balance
            try:
                user.tokens += num_tokens
                db.session.commit()
            except Exception as e:
                print(f"Error updating user's token balance: {e}")
                db.session.rollback()
                raise
        else:
            raise stripe.error.CardError("Charge was not successful.")

    except stripe.error.CardError as e:
        # You might want to handle the error, e.g., notify the user or retry the task
        self.retry(exc=e, countdown=60 * 5, max_retries=3)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        raise
    
    
@celery.task
def send_password_reset_email(user_id):
    # Retrieve the user using Flask-Login's current_user method
    user = User.query.get(user_id)

    # Check if the user exists
    if user is None:
        print("User not found.")
        return "User not found."

    # Generate a secure token for password reset
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    token = serializer.dumps(user.email, salt=current_app.config['SECURITY_PASSWORD_SALT'])

    # Set an expiry time for the token
    expiry = 3600  # 1 hour

    # Create a password reset URL with the token
    reset_url = url_for('main.reset_password', token=token, _external=True)

    # Render an HTML template for the email body
    html = render_template('email/reset_password.html', reset_url=reset_url)

    # Create a more relevant subject for the email
    subject = "Password Reset Request"

    msg = Message(subject, recipients=[user.email], html=html)  # recipient's email

    # Send the email and handle any errors
    try:
        mail.send(msg)
    except Exception as e:
        if isinstance(e, BadSignature):
            print("Invalid token.")
        elif isinstance(e, SignatureExpired):
            print("Token has expired.")
        else:
            print(f"An unexpected error occurred: {e}")
        raise

@celery.task
def send_email_async(search_data, recipient):
    logger.debug("Entered send_email_async()")
    if search_data:
        logger.debug("Search data found")
        # Directly access the emails, phones, and urls from the dictionary
        emails = search_data.get("emails", [])
        phones = search_data.get("phones", [])
        urls = search_data.get("urls", [])

        if emails or phones or urls:
            logger.debug("Emails, phones, or URLs found in search data")
            msg = Message("Search Result", recipients=[recipient])  # recipient's email
            msg.body = "Here is your search result: \n"

            # Add URLs, emails, and phones to the email body
            if urls:
                logger.debug("URLs found in search data")
                msg.body += f"URLs: {', '.join(urls)}\n"
            if emails:
                logger.debug("Emails found in search data")
                msg.body += f"Emails: {', '.join(emails)}\n"
            if phones:
                logger.debug("Phones found in search data")
                msg.body += f"Phones: {', '.join(phones)}"

            logger.debug("Sending email")
            mail.send(msg)
        else:
            logger.warning("No emails, phones, or URLs found in search data")
    else:
        logger.warning("No search data provided")


""" @celery.task
def send_email_async(search_result, recipient):
    
    if search_result is not None:
        
        contact_info = search_result.contact_info
        
        if contact_info is not None:
        
            emails = [email.email for email in contact_info.emails]
            phones = [phone.phone for phone in contact_info.phones]

            msg = Message("Search Result", recipients=[recipient])  # recipient's email
            msg.body = "Here is your search result: \n" 
            msg.body += f"URL: {search_result.url}\n"
            msg.body += f"Emails: {', '.join(emails)}\n"
            msg.body += f"Phones: {', '.join(phones)}"
            
            mail.send(msg)
    else:
        print(f"No search result found with id {search_result}")
 """
