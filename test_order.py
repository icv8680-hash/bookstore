"""
测试订单和下单流程
这里包含了真实业务场景的各种情况
"""
import pytest
from book import BookStore
from order import Order, OrderService


# ============================================================
# 测试 Order 类（单个订单）
# ============================================================

class TestOrder:

    def test_normal_order_total(self):
        """
        场景：普通顾客买书，计算总价
        张三买了 2 本 Python(59.9元) + 1 本 Java(79元)
        总价 = 59.9 * 2 + 79 * 1 = 198.8
        """
        order = Order("ORD0001", "张三", is_vip=False)
        order.add_item("Python入门", 2, 59.9)
        order.add_item("Java指南", 1, 79.0)

        total = order.get_total_price()

        assert total == 198.8

    def test_vip_order_discount(self):
        """
        场景：VIP 顾客打 8 折
        李四（VIP）买了 1 本 100 元的书
        总价 = 100 * 0.8 = 80
        """
        order = Order("ORD0002", "李四", is_vip=True)
        order.add_item("贵书", 1, 100.0)

        total = order.get_total_price()

        assert total == 80.0

    def test_vip_multi_items(self):
        """
        场景：VIP 买多本
        50元 * 2 + 100元 * 1 = 200 → 打8折 = 160
        """
        order = Order("ORD0003", "王五", is_vip=True)
        order.add_item("书A", 2, 50.0)
        order.add_item("书B", 1, 100.0)

        total = order.get_total_price()

        assert total == 160.0

    def test_empty_order(self):
        """场景：空订单，总价应该是 0"""
        order = Order("ORD0004", "赵六")

        assert order.get_total_price() == 0


# ============================================================
# 测试 OrderService（下单完整流程）
# ============================================================

class TestOrderService:

    @pytest.fixture
    def service(self):
        """
        每个测试开始前，自动准备好：
        一个书店，里面有 3 本书，然后创建订单服务
        """
        store = BookStore()
        store.add_book("Python入门", 59.9, 50)    # 50本
        store.add_book("Java指南", 79.0, 30)      # 30本
        store.add_book("算法导论", 128.0, 3)      # 只有3本！
        return OrderService(store)

    # ---------- 正常下单 ----------

    def test_place_order_success(self, service):
        """
        场景：张三买 2 本 Python入门
        期望：订单创建成功，库存从 50 变 48
        """
        order = service.place_order("张三", [("Python入门", 2)])

        # 验证订单
        assert order.order_id == "ORD0001"
        assert order.customer_name == "张三"
        assert order.get_total_price() == 119.8  # 59.9 * 2

        # 验证库存确实减少了
        book = service.bookstore.find_book("Python入门")
        assert book.stock == 48  # 50 - 2

    def test_place_order_multiple_books(self, service):
        """
        场景：一次买多种书
        李四买 1 本 Python(59.9) + 2 本 Java(79.0)
        总价 = 59.9 + 79 * 2 = 217.9
        """
        order = service.place_order("李四", [
            ("Python入门", 1),
            ("Java指南", 2),
        ])

        assert order.get_total_price() == 217.9
        assert len(order.items) == 2

    def test_vip_discount(self, service):
        """
        场景：VIP 顾客下单，应该自动打 8 折
        VIP 买 1 本 100 的算法导论(128元)
        总价 = 128 * 0.8 = 102.4
        """
        order = service.place_order("VIP王", [("算法导论", 1)], is_vip=True)

        assert order.get_total_price() == 102.4

    # ---------- 异常场景 ----------

    def test_book_not_exists(self, service):
        """
        场景：买一本书店里没有的书
        期望：报错"书籍不存在"
        """
        with pytest.raises(ValueError, match="不存在"):
            service.place_order("张三", [("量子力学", 1)])

    def test_insufficient_stock(self, service):
        """
        场景：算法导论只有 3 本，但想买 5 本
        期望：报错"库存不足"
        """
        with pytest.raises(ValueError, match="库存不足"):
            service.place_order("张三", [("算法导论", 5)])

    def test_empty_shopping_list(self, service):
        """
        场景：提交空的购物车
        期望：报错"购物清单不能为空"
        """
        with pytest.raises(ValueError, match="购物清单不能为空"):
            service.place_order("张三", [])

    def test_stock_not_changed_on_failure(self, service):
        """
        场景：买两本书，第二本库存不足
        期望：两本都不扣库存（要么全成功，要么全失败）

        这是工业测试的重要场景：验证"原子性"
        """
        # Python入门有50本，算法导论只有3本
        with pytest.raises(ValueError):
            service.place_order("张三", [
                ("Python入门", 2),     # 这本够
                ("算法导论", 999),     # 这本不够 → 整个订单失败
            ])

        # 验证 Python入门 的库存没有被扣
        python_book = service.bookstore.find_book("Python入门")
        assert python_book.stock == 50  # 还是 50，没变

    # ---------- 查询功能 ----------

    def test_get_order(self, service):
        """测试：下单后能查到订单"""
        order = service.place_order("张三", [("Python入门", 1)])

        found = service.get_order(order.order_id)

        assert found is not None
        assert found.customer_name == "张三"

    def test_get_order_not_found(self, service):
        """测试：查不存在的订单返回 None"""
        result = service.get_order("ORD9999")
        assert result is None

    # ---------- 营收统计 ----------

    def test_total_revenue(self, service):
        """
        场景：多个顾客下单，统计总营收
        订单1: 普通顾客，59.9 * 2 = 119.8
        订单2: VIP 顾客，79 * 1 * 0.8 = 63.2
        总营收 = 119.8 + 63.2 = 183.0
        """
        service.place_order("张三", [("Python入门", 2)], is_vip=False)
        service.place_order("李四", [("Java指南", 1)], is_vip=True)

        revenue = service.get_total_revenue()

        assert revenue == 183.0

    # ---------- 连续操作测试 ----------

    def test_multiple_orders_reduce_stock(self, service):
        """
        场景：多人连续买同一本书，库存持续减少
        算法导论只有 3 本：
            第1个人买1本 → 剩2本
            第2个人买2本 → 剩0本
            第3个人再买 → 应该报错
        """
        service.place_order("A", [("算法导论", 1)])
        service.place_order("B", [("算法导论", 2)])

        # 现在库存是 0 了
        book = service.bookstore.find_book("算法导论")
        assert book.stock == 0

        # 第3个人再买就不行了
        with pytest.raises(ValueError, match="库存不足"):
            service.place_order("C", [("算法导论", 1)])
