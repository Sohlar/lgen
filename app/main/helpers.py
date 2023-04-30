def get_profile_css_class(user):
    if user.subscription == 'free':
        return 'profile-free'
    elif user.subscription == 'silver':
        return 'profile-silver'
    elif user.subscription == 'gold':
        return 'profile-gold'
    else:
        return 'profile-default'  # Fallback CSS class in case of an unknown subscription
