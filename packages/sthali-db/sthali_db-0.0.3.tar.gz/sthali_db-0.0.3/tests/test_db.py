import unittest
import unittest.mock

import sthali_db.db

module = sthali_db.db


class TestDBSpecification(unittest.IsolatedAsyncioTestCase):
    async def test_return(self) -> None:
        db_spec = module.DBSpecification(path="test_path", client="tinydb")  # type: ignore

        self.assertEqual(db_spec.path, "test_path")
        self.assertEqual(db_spec.client.name, "tinydb")


class TestDB(unittest.IsolatedAsyncioTestCase):
    class MockDefaultClient:
        insert_one = unittest.mock.AsyncMock(return_value="insert_one")
        select_one = unittest.mock.AsyncMock(return_value="select_one")
        update_one = unittest.mock.AsyncMock(return_value="update_one")
        delete_one = unittest.mock.AsyncMock(return_value="delete_one")
        select_many = unittest.mock.AsyncMock(return_value="select_many")

    @unittest.mock.patch("sthali_db.clients.default.DefaultClient")
    def setUp(self, mocked_client: unittest.mock.MagicMock) -> None:
        mocked_client.return_value = self.MockDefaultClient()
        db_spec = module.DBSpecification("test_path", "default")  # type: ignore
        self.db = module.DB(db_spec, "table")  # type: ignore
        default = module.enum_clients_config.clients_map["default"]
        self.resource_id = default.ResourceId
        self.resource_obj = default.ResourceObj
        self.paginate_parameters = default.dependencies.PaginateParameters

    async def test_insert_one(self) -> None:
        result = await self.db.insert_one(self.resource_id, self.resource_obj)

        self.assertEqual(result, "insert_one")

    async def test_select_one(self) -> None:
        result = await self.db.select_one(self.resource_id)

        self.assertEqual(result, "select_one")

    async def test_update_one(self) -> None:
        result = await self.db.update_one(self.resource_id, self.resource_obj)

        self.assertEqual(result, "update_one")

    async def test_delete_one(self) -> None:
        result = await self.db.delete_one(self.resource_id)

        self.assertEqual(result, "delete_one")

    async def test_select_many(self) -> None:
        result = await self.db.select_many(self.paginate_parameters)

        self.assertEqual(result, "select_many")
