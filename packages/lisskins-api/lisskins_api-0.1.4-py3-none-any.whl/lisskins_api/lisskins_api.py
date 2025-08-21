import aiohttp


class LisSkinsAPIClient:
    """
    Singleton class for interacting with Lis Skins API
    https://lis-skins.stoplight.io/docs/lis-skins/
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Override __new__ to ensure singleton behavior while passing arguments correctly
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, api_key: str):
        """
        Initialize the client with an API key

        :param api_key: Lis-Skins API key
        """
        self.api_key = api_key
        self.endpoint = 'https://api.lis-skins.com/v1/'


    async def user_balance(self):
        """
        Fetch user's balance from the API
        """

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.endpoint + 'user/balance', headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    else:
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def buy_skin(
            self, item_ids: list[int], partner: str, token: str, max_price: int = None,
            custom_id: str = None, skip_unavailable: bool = None
    ):
        """
        Buy skin(s) for a specific user

        :param item_ids: ID's of skins. Max: 100
        :param partner: Value from user\\'s Trade URL
        :param token: Value from user\\'s Trade URL
        :param max_price: limit to purchase of a skin(s)
        :param custom_id: Optional custom id for your system to prevent double purchases
        :param skip_unavailable: If this parameter is specified, unavailable skins will be ignored
        """

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "ids": item_ids,
            "partner": partner,
            "token": token,
        }

        if max_price is not None:
            payload['max_price'] = max_price
        if custom_id is not None:
            payload['custom_id'] = custom_id
        if skip_unavailable is not None:
            skip_unavailable['skip_unavailable'] = skip_unavailable


        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.endpoint + 'market/buy', json=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 400:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def search_skins(
            self, game: str, cursor: str = None, float_from: int = None, float_to: int = None,
            names: list[str] = None, only_unlocked: int = 0, price_from: int = None, price_to: int = None,
            sort_by: str = None, unlock_days: list[int] = None
    ):
        """
        Search skins available for purchase

        :param game: Game (csgo, dota2, rust)
        :param cursor: Cursor for pagination ("meta.next_cursor" value response)
        :param float_from: Skin float starts from
        :param float_to: Skin float ends
        :param names: Skin names to search for
        :param only_unlocked: Search only by unlocked skins (0, 1)
        :param price_from: Skin price starts from
        :param price_to: Skin price ends
        :param sort_by: Sort fields (oldest, newest, lowest_price, highest_price)
        :param unlock_days: An array with days of skin to be unlocked (min: 0, max: 8, ex. [1,3,5])
        """

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            'game': game,
        }

        if cursor is not None:
            payload['cursor'] = cursor
        if float_from is not None:
            payload['float_from'] = float_from
        if float_to is not None:
            payload['float_to'] = float_to
        if names is not None:
            payload['names[]'] = names
        if only_unlocked is not None:
            payload['only_unlocked'] = only_unlocked
        if price_from is not None:
            payload['price_from'] = price_from
        if price_to is not None:
            payload['price_to'] = price_to
        if sort_by is not None:
            payload['sort_by'] = sort_by
        if unlock_days is not None:
            payload['unlock_days[]'] = unlock_days


        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.endpoint + 'market/search', params=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds')
                return None
        return None


    async def purchased_skins_info(self, purchase_ids: list[int], custom_ids: list[str] = None):
        """
        Get information about purchased skins and its statuses

        :param purchase_ids: An array of custom_id that were transferred when purchasing skins (max: 200)
        :param custom_ids: An array of purchase_id that were received when purchasing skins (max: 200)
        """

        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            'purchase_ids[]': purchase_ids
        }

        if custom_ids is not None:
            payload['custom_ids[]'] = custom_ids

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.endpoint + 'market/info', params=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None

            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def purchase_skin_history(self, page: int = None, end_unix_time: int = None, start_unix_time: int = None):
        """
        Get purchase history information

        :param page: Page number for pagination
        :param end_unix_time: UNIX end date
        :param start_unix_time: UNIX start date
        """

        headers = {
            'Accept': "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {}

        if page is not None:
            payload['page'] = page
        if end_unix_time is not None:
            payload['end_unix_time'] = end_unix_time
        if start_unix_time is not None:
            payload['start_unix_time'] = start_unix_time

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.endpoint + 'market/history', params=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def withdraw_unlocked_skins(
            self, purchase_ids: list[int] = None, custom_ids: list[str] = None, partner: str = None, token: str = None
    ):
        """
        Withdraw all unlocked items

        :param purchase_ids: An array of purchase_id of purchases to be displayed (max:200)
        :param custom_ids: An array of custom_id of purchases to be displayed (max: 200)
        :param partner: If you want to change the user to whom to send skins from this purchase,
        then pass this parameter and the token parameter from the Trade URL
        :param token: If your Trade URL for the user to send skins to is outdated, you can change it
        """

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {}

        if purchase_ids is not None:
            payload['purchase_ids[]'] = purchase_ids
        if custom_ids is not None:
            payload['custom_ids[]'] = custom_ids
        if partner is not None:
            payload['partner'] = partner
        if token is not None:
            payload['token'] = token

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.endpoint + 'market/withdraw-all', json=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 400:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def withdraw_skins_from_specific_purchase(
            self, purchase_id: int = None, custom_id: str = None, partner: str = None, token: str = None
    ):
        """
        Withdraw all unlocked items

        :param purchase_id: Optional custom_id, which was transferred when purchasing the skin
        :param custom_id: Optional purchase_id, which was returned when purchasing the skin
        :param partner: If you want to change the user to whom to send skins from this purchase,
        then pass this parameter and the token parameter from the Trade URL
        :param token: If your Trade URL for the user to send skins to is outdated, you can change it
        """

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {}

        if purchase_id is not None:
            payload['purchase_id'] = purchase_id
        if custom_id is not None:
            payload['custom_id'] = custom_id
        if partner is not None:
            payload['partner'] = partner
        if token is not None:
            payload['token'] = token

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.endpoint + 'market/withdraw', json=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 400:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def return_locked_skins(self, purchase_id: int = None, custom_id: str = None, id: int = None):
        """
        Return locked skins (3% commission will be charged)

        :param purchase_id: Optional custom_id, which was transferred when purchasing the skin(s)
        :param custom_id: Optional purchase_id, which was returned when purchasing the skin(s)
        :param id: Used with custom_id or purchase_id.
        In order to return a specific skin if there were several of them in the purchase.
        """

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {}

        if custom_id is not None:
            payload['custom_id'] = custom_id
        if purchase_id is not None:
            payload['purchase_id'] = purchase_id
        if id is not None:
            payload['id'] = id

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(self.endpoint + 'market/withdraw', json=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 400:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None


    async def check_skin_availability(self, ids: list[int]):
        """
        Check the availability of a skin for purchase by its ID.

        :param ids: Skin IDs that need to be checked. (Max: 100)
        """

        headers = {
            'Accept': "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "ids[]": ids
        }

        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.endpoint + 'market/check-availability', params=payload, headers=headers, timeout=15) as response:
                    if response.status == 200:
                        response_data = await response.json()
                        return response_data
                    elif response.status == 422:
                        response_data = await response.json()
                        return response_data
                    else:
                        print('Unexpected error occurred')
                        return None
            except aiohttp.ServerTimeoutError:
                print('The server did not respond within 15 seconds.')
                return None
        return None
