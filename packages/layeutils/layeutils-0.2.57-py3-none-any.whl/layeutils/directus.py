
from datetime import datetime

from directus_sdk_py import DirectusClient, DirectusQueryBuilder, DOp


class TradingRecord():
    """Trading Record Class

    Attributes: id, open_time, close_time, symbol, direction, quantity, filled_price, commission, comments

    """

    id: str
    daily_journal: str
    symbol: str
    trading_time: datetime
    direction: str
    quantity: float
    filled_price: float
    commission: float
    comments: str

    def load_from_directus_item_obj(self, directus_item_obj: dict):
        """ Load TradingRecord instance from a Directus object.

        Args:
            directus_obj (dict): Directus object containing trading record data
        """
        self.id = directus_item_obj.get('id')
        self.daily_journal = directus_item_obj.get('daily_journal')
        self.symbol = directus_item_obj.get('symbol')
        self.trading_time = datetime.fromisoformat(directus_item_obj.get('trading_time'))
        self.direction = int(directus_item_obj.get('direction'))
        self.quantity = float(directus_item_obj.get('quantity'))
        self.filled_price = float(directus_item_obj.get('filled_price'))
        self.commission = float(directus_item_obj.get('commission'))
        self.comments = directus_item_obj.get('comments')

    def to_directus_item_obj(self):
        """ Convert the TradingRecord instance to a dictionary.

        Returns:
            _type_: _description_
        """
        result = {}
        if hasattr(self, 'id'):
            result['id'] = self.id
        if hasattr(self, 'daily_journal'):
            result['daily_journal'] = self.daily_journal
        if hasattr(self, 'symbol'):
            result['symbol'] = self.symbol
        if hasattr(self, 'trading_time'):
            result['trading_time'] = self.trading_time.isoformat()
        if hasattr(self, 'direction'):
            result['direction'] = self.direction
        if hasattr(self, 'quantity'):
            result['quantity'] = str(self.quantity)
        if hasattr(self, 'filled_price'):
            result['filled_price'] = str(self.filled_price)
        if hasattr(self, 'commission'):
            result['commission'] = str(self.commission)
        if hasattr(self, 'comments'):
            result['comments'] = self.comments
        return result

    def create_trading_record(self, client: DirectusClient):
        """Create a new trading record in Directus.
        Args:
            client (DirectusClient): Directus Client instance
        Returns:
            The created trading record item
        """
        return client.create_item(
            collection_name='trading_record',
            item_data=self.to_directus_item_obj()
        )

    def update_trading_record(self, client: DirectusClient):
        """Update an existing trading record in Directus.

        Args:
            client (DirectusClient): Directus Client instance
        Returns:
            The updated trading record item
        """
        return client.update_item(
            collection_name='trading_record',
            item_id=self.id,
            item_data=self.to_directus_item_obj()
        )

    def delete_trading_record(self, client: DirectusClient):
        """Delete a trading record from Directus.

        Args:
            client (DirectusClient): Directus Client instance
        """
        client.delete_item(
            collection_name='trading_record',
            item_id=self.id
        )


def get_directus_client(
    access_token: str,
    url: str = 'http://directus:8055'
) -> DirectusClient:
    """Get Directus Client

    Returns:
        DirectusClient: Directus Client instance
    """
    return DirectusClient(url=url, token=access_token)


def create_item_to_collection(
    client: DirectusClient,
    collection_name: str,
    directus_item_obj: dict
):
    return client.create_item(
        collection_name=collection_name,
        item_data=directus_item_obj
    )


def update_item(
    client: DirectusClient,
    collection_name: str,
    item_id: str,
    field_value: dict
):
    """update existing item with field and value dict

    Args:
        client (DirectusClient): _description_
        collection_name (str): _description_
        item_id (str): _description_
        field_value (dict): eg. {'title': 'Updated Title'}

    Returns:
        _type_: _description_
    """
    return client.update_item(
        collection_name=collection_name,
        item_id=item_id,
        item_data=field_value
    )


def delete_item(
    client: DirectusClient,
    collection_name: str,
    item_id: str
):
    client.delete_item(
        collection_name=collection_name,
        item_id=item_id
    )


def get_items_from_collection(
        client: DirectusClient,
        collection_name: str,
        query_builder: DirectusQueryBuilder = None):
    """Get items from a Directus collection.

    Args:
        client (DirectusClient): Directus Client instance
        collection_name (str): Name of the collection to fetch items from
        query (dict, optional): Query parameters to filter items. Defaults to None.
            for query build example, check method `build_query_by_datetime_range`

    Returns:
        List of items in the specified collection
    """
    items = []
    count = 0
    while True:
        if query_builder:
            batch_items = client.get_items(
                collection_name,
                query_builder.limit(100).offset(count).build()
            )
        else:
            batch_items = client.get_items(
                collection_name,
                DirectusQueryBuilder().limit(100).offset(count).build()
            )
        if not isinstance(batch_items, list):
            raise TypeError(f'Item返回不是list类型，batch_items：{batch_items}')
        if len(batch_items) == 0:
            break
        items.extend(batch_items)
        count += 100
    return items


def build_query_by_datetime_range(
        directus_collection_field: str,
        start_time: datetime,
        end_time: datetime) -> DirectusQueryBuilder:
    """Build a query to filter items by a datetime range.
    Args:
        directus_collection_field (str): The field in the Directus collection to filter by datetime
        start_time (datetime): Start of the datetime range
        end_time (datetime): End of the datetime range
    Returns:
        DirectusQueryBuilder Object
    """
    return DirectusQueryBuilder().field(
        directus_collection_field,
        DOp.BETWEEN,
        [start_time.isoformat(), end_time.isoformat()])
