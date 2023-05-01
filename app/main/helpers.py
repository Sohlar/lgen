def get_profile_css_class(user):
    if not user.is_authenticated:
        return ''
    if user.subscription == 'free':
        return 'text-primary'
    elif user.subscription == 'silver':
        return 'text-success'
    elif user.subscription == 'gold':
        return 'text-danger'
    else:
        return ''  # Fallback CSS class in case of an unknown subscription
