from app.extensions import db, celery
from app.services.search_engines import GoogleSearch
from app.services.search_engine_factory import SearchEngineFactory
from app.main.models import SearchResult, ContactInfo, Email, Phone
from flask_mail import Message
from app import celery, mail

@celery.task(bind=True, name="main.search_engine_task")
def search_engine_task(self, engine_str, search_history_id, query, cost):
    results = SearchEngineFactory.create_search_engine(engine=engine_str).search(query=query, num_urls = cost)
    print('RUNNING TASK NOWWWWWW')
    for result in results:
        if (result['email'] or result['phone']):
            emails = result['email'] 
            phones = result['phone'] 
            print(emails)
            print(phones)
            print('---------\n')
            search_result = SearchResult(search_history_id=search_history_id, url=result['url'])
            print(f'*Search Result: {search_result}')
            db.session.add(search_result)
            db.session.flush()
            contact_info = ContactInfo(search_result_id=search_result.id)
            print(f'*Contact Info: {contact_info}')
            db.session.add(contact_info)
            db.session.flush()

            #Not sure why we are looping through run debugger to check if emails = []
            for email_addr in emails:
                email = Email(contact_info_id=contact_info.id, email=email_addr)
                db.session.add(email)
            for phone_addr in phones:
                phone = Phone(contact_info_id=contact_info.id, phone=phone_addr)
                db.session.add(phone)
            print('Search Done')
    db.session.commit()

@celery.task
def send_email_async(search_result_id, recipient):
    msg = Message("Search Result", recipients=[recipient])  # recipient's email
    msg.body = "Here is your search result: \n" + str(search_result_id)
    mail.send(msg)
