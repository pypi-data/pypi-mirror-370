from supabase import create_client, Client
from supabase.client import ClientOptions


class Connection:

    def __init__(self):
        url: str = "https://tvpehjbqxpiswkqszwwv.supabase.co"
        key: str = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InR2cGVoamJxeHBpc3drcXN6d3d2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTY0NTEzODksImV4cCI6MjAxMjAyNzM4OX0.LZW0i9HU81lCdyjAdqjwwF4hkuSVtsJsSDQh7blzozw"
        self.supabase: Client = create_client(
            url, key,
            options=ClientOptions(
                auto_refresh_token=False,
                postgrest_client_timeout=40,
                storage_client_timeout=40,
                schema="xerenity",
            ))

    def login(self, username, password):
        """

        Inicia sesion con el servidor de xerenity

        :param username: Usuario
        :param password: contrasena
        :return:
        """
        try:
            data = self.supabase.auth.sign_in_with_password(
                {
                    "email": username,
                    "password": password}
            )
            return data

        except Exception as er:
            return str(er)

    def get_all_series(self):
        """

        :return:
        """
        try:
            data = self.supabase.from_('search_mv').select(
                'source_name,grupo,description,display_name,ticker').execute().data
            return data
        except Exception as er:
            return str(er)

    def read_serie(self, ticker: str):
        """

        Funcion que retorna los valores de la serie deseada, si la serie no es encontrada
        se retorna un contenedor vacio

        :param ticker: Identificador unico de la serie a leer
        :return:
        """
        try:
            data = self.supabase.rpc('search', {"ticket": ticker}).execute().data
            if 'data' in data:
                return data['data']
            return data
        except Exception as er:
            return str(er)

    def call_rpc(self, rpc_name, rpc_body: dict):
        return self.supabase.rpc(rpc_name, rpc_body).execute().data

    def list_loans(self, bank_names: list = None):
        """
        Lee la lista entera de creditos en xerenity
        :return:
        """
        try:

            loans_list = self.call_rpc('get_loans', {
                "bank_name_filter": bank_names
            })

            return loans_list

        except Exception as er:
            return str(er)

    def create_loan(self,
                    start_date: str,
                    bank: str,
                    number_of_payments: int,
                    original_balance: float,
                    periodicity: str,
                    interest_rate: float,
                    type: str,
                    days_count: str = None,
                    grace_type: str = None,
                    grace_period: int = None,
                    min_period_rate: float = None,
                    loan_identifier: str = None,
                    ):

        try:

            return self.supabase.rpc('create_credit', {
                "start_date": start_date,
                "bank": bank,
                "number_of_payments": number_of_payments,
                "original_balance": original_balance,
                "periodicity": periodicity,
                "interest_rate": interest_rate,
                "type": type,
                "days_count": days_count,
                "grace_type": grace_type,
                "grace_period": grace_period,
                "min_period_rate": min_period_rate,
                "loan_identifier": loan_identifier,
            }).execute().data

        except Exception as er:
            return str(er)
