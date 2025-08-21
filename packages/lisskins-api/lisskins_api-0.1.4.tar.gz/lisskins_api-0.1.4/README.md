## ▌ Asynchronous Module for Interacting with the Lis Skins API

This project is an asynchronous Python module designed to facilitate interaction with the LIS Skins API. The module allows users to retrieve account balances, purchase skins, view their purchase histories, withdraw unlocked skins, and return locked ones, perform all actions that Lis Skins API allows. 

> Current API documentation can be found [here](https://lis-skins.stoplight.io/docs/lis-skins/)

## ▌ Installation & Usage

Install the library using pip:

```pip install lisskins_api```

### Example usage:

```
from lisskins_api import LisSkinsAPIClient


async def main():
    client = LisSkinsAPIClient('<api_key>')

    # Get account balance
    balance = await client.user_balance()

    # Search skin to buy
    search_skins = await client.search_skins(
        'csgo', price_from=1, price_to=10, float_from=0.9, sort_by='lowest_price',
        only_unlocked=1, names=['Glock-18 | Bullet Queen (Battle-Scarred)']
    )

    # Buy a skin
    buy_skin = await client.buy_skin(
        item_ids=[240978929], partner='<part of trade link>', token='<part of trade link>'
    )

    # Check status purchased skin 
    purchased_skin_info = await client.purchased_skins_info(purchase_ids=[39999999])

    # Withdraw a skin
    withdraw_skin = await client.withdraw_skins_from_specific_purchase(purchase_id=39999999)
  
  
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

## ▌ License

The project is distributed under the MIT License. Detailed information can be found in the LICENSE file.

---
If you have any questions or need help with anything, feel free to reach out me or check out the official Lis Skins API docs.
