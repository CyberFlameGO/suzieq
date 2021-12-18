import logging
from pathlib import Path
from typing import Callable, Dict, List
import aiofiles
import yaml
from suzieq.poller.worker.inventory.inventory import Inventory
from suzieq.shared.exceptions import InventorySourceError

logger = logging.getLogger(__name__)


class StaticManager(Inventory):
    """StaticManager allows to import the inventory from files
    generated by the controller
    """

    def __init__(self, add_task_fn: Callable, **kwargs) -> None:
        worker_id = kwargs.pop('worker-id', '0')
        inventory_file_name = kwargs.pop('inventory-file-name', 'inv')

        inv_path = kwargs.get('inventory-path',
                              'suzieq/.poller/inventory/static_inventory')
        self._inventory_file = Path(inv_path).joinpath(
            f'{inventory_file_name}_{worker_id}.yml').resolve()

        if not self._inventory_file.is_file():
            raise InventorySourceError(
                f'No inventory found at {self._inventory_file}')

        super().__init__(add_task_fn, **kwargs)

    async def _get_device_list(self) -> List[Dict]:

        async with aiofiles.open(str(self._inventory_file), "r") as out_file:
            read_content = await out_file.read()
            inventory = yaml.safe_load(read_content)

        if not isinstance(inventory, dict):
            raise InventorySourceError('Invalid inventory format. Expected'
                                       f'dict, found {type(inventory)}')

        return inventory.values()
