"""
测试书籍相关功能
每个 test_ 函数就是一个测试用例
"""
import pytest
from book import Book, BookStore


# ============================================================
# 测试 Book 类（一本书）
# ============================================================

class TestBook:
    """把相关测试放在一个 class 里，方便组织"""

    def test_create_book(self):
        """测试：能正常创建一本书"""
        book = Book("Python入门", 59.9, 100)

        assert book.name == "Python入门"
        assert book.price == 59.9
        assert book.stock == 100

    def test_price_must_be_positive(self):
        """测试：价格不能为 0 或负数"""
        with pytest.raises(ValueError, match="价格必须大于0"):
            Book("坏书", 0, 10)

        with pytest.raises(ValueError, match="价格必须大于0"):
            Book("坏书", -10, 10)

    def test_stock_cannot_be_negative(self):
        """测试：库存不能为负数"""
        with pytest.raises(ValueError, match="库存不能为负数"):
            Book("坏书", 10, -5)

    def test_is_available(self):
        """测试：有库存就可以买"""
        book = Book("有货的书", 30, 5)
        assert book.is_available() is True

    def test_is_not_available(self):
        """测试：库存为 0 就不能买"""
        book = Book("卖光的书", 30, 0)
        assert book.is_available() is False

    def test_reduce_stock_success(self):
        """测试：正常扣库存"""
        book = Book("好书", 50, 10)

        book.reduce_stock(3)

        assert book.stock == 7  # 10 - 3 = 7

    def test_reduce_stock_insufficient(self):
        """测试：库存不足时应该报错，而不是变成负数"""
        book = Book("稀缺书", 100, 2)

        with pytest.raises(ValueError, match="库存不足"):
            book.reduce_stock(5)  # 只有2本，要买5本

        assert book.stock == 2  # 确认库存没变

    def test_reduce_stock_invalid_quantity(self):
        """测试：购买数量不能为 0 或负数"""
        book = Book("好书", 50, 10)

        with pytest.raises(ValueError, match="购买数量必须大于0"):
            book.reduce_stock(0)

        with pytest.raises(ValueError, match="购买数量必须大于0"):
            book.reduce_stock(-1)


# ============================================================
# 测试 BookStore 类（书店）
# ============================================================

class TestBookStore:

    @pytest.fixture
    def store(self):
        """
        pytest.fixture 是"测试夹具"
        简单理解：每个测试开始前，自动准备好一个装了书的书店
        避免每个测试里都写一遍 store = BookStore()
        """
        store = BookStore()
        store.add_book("Python入门", 59.9, 50)
        store.add_book("Java指南", 79.0, 30)
        store.add_book("算法导论", 128.0, 10)
        return store

    def test_add_new_book(self):
        """测试：添加新书"""
        store = BookStore()
        store.add_book("新书", 30, 20)

        assert store.get_book_count() == 1
        book = store.find_book("新书")
        assert book.price == 30
        assert book.stock == 20

    def test_add_existing_book_increases_stock(self):
        """测试：已有的书再添加，应该增加库存而不是覆盖"""
        store = BookStore()
        store.add_book("Python入门", 59.9, 50)
        store.add_book("Python入门", 59.9, 30)  # 再添加 30 本

        book = store.find_book("Python入门")
        assert book.stock == 80  # 50 + 30

    def test_find_book_exists(self, store):
        """测试：查找存在的书"""
        book = store.find_book("Python入门")

        assert book is not None
        assert book.name == "Python入门"

    def test_find_book_not_exists(self, store):
        """测试：查找不存在的书"""
        book = store.find_book("不存在的书")

        assert book is None

    def test_list_available_books(self, store):
        """测试：列出有库存的书"""
        # 把"算法导论"卖光
        algo = store.find_book("算法导论")
        algo.stock = 0

        available = store.list_available_books()

        assert len(available) == 2  # 只剩2本有库存
        names = [b.name for b in available]
        assert "算法导论" not in names

    def test_get_book_count(self, store):
        """测试：书的种类数"""
        assert store.get_book_count() == 3


# ============================================================
# 参数化测试：一组数据跑多个用例（工业常用）
# ============================================================

class TestBookParametrize:

    @pytest.mark.parametrize("stock, buy, expected_remaining", [
        (100, 1, 99),     # 买1本
        (100, 50, 50),    # 买50本
        (100, 100, 0),    # 全买光
        (5, 3, 2),        # 小库存
    ])
    def test_reduce_stock_various(self, stock, buy, expected_remaining):
        """参数化测试：用不同数据测同一个功能"""
        book = Book("测试书", 10, stock)
        book.reduce_stock(buy)
        assert book.stock == expected_remaining
