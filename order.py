from book import BookStore


class Order:
    """一个订单"""

    def __init__(self, order_id, customer_name, is_vip=False):
        """
        order_id:      订单号，比如 "ORD001"
        customer_name: 顾客名字，比如 "张三"
        is_vip:        是不是 VIP 顾客（VIP 打 8 折）
        """
        self.order_id = order_id
        self.customer_name = customer_name
        self.is_vip = is_vip
        self.items = []  # 订单里买了哪些书，每项是 (书名, 数量, 单价)

    def add_item(self, book_name, quantity, unit_price):
        """往订单里添加一项"""
        self.items.append({
            "book_name": book_name,
            "quantity": quantity,
            "unit_price": unit_price,
        })

    def get_total_price(self):
        """
        计算订单总价
        普通顾客：原价
        VIP 顾客：打 8 折
        """
        total = 0
        for item in self.items:
            total += item["quantity"] * item["unit_price"]

        if self.is_vip:
            total = total * 0.8  # VIP 打 8 折

        # 保留两位小数
        return round(total, 2)


class OrderService:
    """订单服务：处理下单的完整流程"""

    def __init__(self, bookstore: BookStore):
        self.bookstore = bookstore
        self.orders = []  # 存所有订单
        self.order_counter = 0  # 订单号计数器

    def place_order(self, customer_name, shopping_list, is_vip=False):
        """
        下单！

        参数说明：
            customer_name: 顾客名字
            shopping_list: 购物清单，格式 [("书名", 数量), ...]
            is_vip:        是否 VIP

        使用举例：
            service.place_order("张三", [("Python入门", 2), ("Java指南", 1)])

        完整流程：
            1. 检查每本书是否存在
            2. 检查库存够不够
            3. 扣减库存
            4. 生成订单
            5. 计算总价（VIP 打折）
        """
        if not shopping_list:
            raise ValueError("购物清单不能为空")

        # === 第1步：先检查所有书，全部OK才往下走 ===
        books_to_buy = []
        for book_name, quantity in shopping_list:
            book = self.bookstore.find_book(book_name)
            if book is None:
                raise ValueError(f"书籍《{book_name}》不存在")
            if quantity > book.stock:
                raise ValueError(
                    f"《{book_name}》库存不足！剩余 {book.stock} 本，你要买 {quantity} 本"
                )
            books_to_buy.append((book, quantity))

        # === 第2步：全部检查通过，开始扣库存 ===
        self.order_counter += 1
        order_id = f"ORD{self.order_counter:04d}"  # 生成订单号：ORD0001
        order = Order(order_id, customer_name, is_vip)

        for book, quantity in books_to_buy:
            book.reduce_stock(quantity)
            order.add_item(book.name, quantity, book.price)

        # === 第3步：保存订单 ===
        self.orders.append(order)
        return order

    def get_order(self, order_id):
        """按订单号查询"""
        for order in self.orders:
            if order.order_id == order_id:
                return order
        return None

    def get_total_revenue(self):
        """计算书店总营收"""
        return sum(order.get_total_price() for order in self.orders)
