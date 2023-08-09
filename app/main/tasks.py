from app.extensions import db, celery
#from app.services.search_engines import GoogleSearch
from app.services.search_engine_factory import SearchEngineFactory
from app.main.models import SearchResult, ContactInfo, Email, Phone, User, SearchHistory
from flask_mail import Message
from app import  celery, mail
from app.services.logger import logger
from app.services.search_3 import GoogleSearch

@celery.task(bind=True, name="main.search_engine_task")
def search_engine_task(self, search_history_id, query, cost, user_id):
    
    logger.debug("Entering celery task")
    
    #results = SearchEngineFactory.create_search_engine(engine=engine_str).search(query=query, num_urls = cost)
    
    gs = GoogleSearch()
    
    results = gs.search(query, num_urls=cost)

    logger.debug('Search ended *\ Adding Results to DB')
    
    try:
        for result in results:
    
            if (result['email'] or result['phone']):

                emails = result['email'] 
                phones = result['phone'] 

                search_result = SearchResult(search_history_id=search_history_id, url=result['url'])
                logger.debug(f'*Search Result: {search_result}')
                db.session.add(search_result)

                contact_info = ContactInfo(search_result_id=search_result.id)
                logger.debug(f'*Contact Info: {contact_info}')
                db.session.add(contact_info)


                for email_addr in emails:
                    email = Email(contact_info_id=contact_info.id, email=email_addr)
                    logger.debug(f"*/ Email Added: {email}")
                    db.session.add(email)

                for phone_addr in phones:
                    phone = Phone(contact_info_id=contact_info.id, phone=phone_addr)
                    logger.debug(f"*/ Phone Added: {phone}")
                    db.session.add(phone)
                    
        db.session.commit()
        
        # Send result emails after the search is complete
        user = User.query.get(user_id)
        
        
        send_email_async(get_most_recent_search_result(user, search_history_id), user.email)
        
    except Exception as e:
        
        db.session.rollback()
        logger.exception("An error Occurred, transaction rolled back", e)
    
    finally:
        
        db.session.close()

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
    
def get_most_recent_search_result(user_id):
    # Retrieve the user instance by user_id
    user = User.query.get(user_id)
    
    if not user:
        print("No user found for the given id.")
        return

    # Get the search history for the user
    search_history = user.search_history

    if not search_history:
        print("No search history found for the given user.")
        return

    # Get the most recent search result from the user's search history
    most_recent_search_result = search_history.results.order_by(SearchResult.id.desc()).first()

    if most_recent_search_result:
        return most_recent_search_result
    else:
        print("No search results found for the given search history.")
        return






@celery.task
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




