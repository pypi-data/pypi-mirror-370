class Series:

    def __init__(self, connection):
        self.sup = connection

    def portfolio(self):
        """

        Function para obtener el portafolio completo de series que ofrece Xerenity
        :return: [{{'source_name': str, 'grupo': str, 'description': str, 'display_name':str}]
        """
        return self.sup.get_all_series()

    def search(self, ticker):
        """

        Dado el nombre de una serie, retorna los valores almacenados por Xerenity
        Para obtener el nombre de la serie, puede vistar la pagina web o utilizar la funcion portafolio
        :param ticker:
        :return: [{"time":"fecha","value":valor de la serie en la fecha}]
        """
        return self.sup.read_serie(ticker=ticker)
