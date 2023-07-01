from app.extensions import celery, db
from app.services.search_engines import GoogleSearch, BingSearch
from app.services.search_engine_factory import SearchEngineFactory
from app.main.models import SearchHistory, SearchResult, ContactInfo, Email, Phone

@celery.task(name="main.search_engine_task")
def search_engine_task(engine_str, search_history_id, query, cost):
    results = SearchEngineFactory.create_search_engine(engine_str).search(query=query, num_urls = cost)
    for result in results:
        if (result['email'] or result['phone']):
            emails = result['email'] 
            phones = result['phone'] 
            search_result = SearchResult(search_history_id=search_history_id, url=result['url'])
            db.session.add(search_result)
            db.session.flush()
            contact_info = ContactInfo(search_result_id=search_result.id)
            db.session.add(contact_info)
            db.session.flush()
            for email_addr in emails:
                email = Email(contact_info_id=contact_info.id, email=email_addr)
                db.session.add(email)
            for phone_addr in phones:
                phone = Phone(contact_info_id=contact_info.id, phone=phone_addr)
                db.session.add(phone)
    db.session.commit()