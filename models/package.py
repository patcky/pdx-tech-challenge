class Package(object):
    def __init__(self, params):
        self.id: int = params.get('id')
        self.price_currency = params.get('price_currency')
        self.price_initial = params.get('price_initial')
        self.price_final = params.get('price_final')
        self.price_discount_percent = params.get('price_discount_percent')
        self.price_individual = params.get('price_individual')
        self.platforms_windows = params.get('platforms_windows')
        self.platforms_mac = params.get('platforms_mac')
        self.platforms_linux = params.get('platforms_linux')
        self.release_date_coming_soon = params.get('release_date_coming_soon')
        self.release_date = params.get('release_date')
        self.error = params.get('error')
