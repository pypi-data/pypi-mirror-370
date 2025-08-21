import unittest

import sthali_db.types

module = sthali_db.types


class TestTypes(unittest.IsolatedAsyncioTestCase):
    async def test_get(self) -> None:
        types = module.Types()

        result = types.get("any")
        self.assertEqual(result, module.typing.Any)

    async def test_get_raise_exception(self) -> None:
        types = module.Types()

        with self.assertRaises(AttributeError):
            types.get("custom")

    async def test_set(self) -> None:
        types = module.Types()
        types.set("custom", module.typing.Any)

        result = types.get("custom")
        self.assertEqual(result, module.typing.Any)

    async def test_set_raise_exception(self) -> None:
        types = module.Types()
        types.set("custom", module.typing.Any)

        with self.assertRaises(TypeError):
            types.set("custom", module.typing.Any)

    async def test_pop(self) -> None:
        types = module.Types()
        types.pop("any")
