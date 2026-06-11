class Book:
    """一本书"""

    def __init__(self, name, price, stock):
        """
        name:  书名，比如 "Python入门"
        price: 单价，比如 59.9
        stock: 库存数量，比如 100 本
        """
        if price <= 0:
            raise ValueError("价格必须大于0")
        if stock < 0:
            raise ValueError("库存不能为负数")

        self.name = name
        self.price = price
        self.stock = stock

    def is_available(self):
        """这本书还有没有库存"""
        return self.stock > 0

    def reduce_stock(self, quantity):
        """
        扣减库存
        比如有人买了 3 本，库存从 100 变成 97
        """
        if quantity <= 0:
            raise ValueError("购买数量必须大于0")
        if quantity > self.stock:
            raise ValueError(f"库存不足！剩余 {self.stock} 本，你要买 {quantity} 本")

        self.stock -= quantity

    def __repr__(self):
        return f"《{self.name}》 ¥{self.price} 库存:{self.stock}"


class BookStore:
    """书店：管理所有书籍"""

    def __init__(self):
        self.books = {}  # 用字典存书，key 是书名

    def add_book(self, name, price, stock):
        """
        上架一本新书
        比如：store.add_book("Python入门", 59.9, 100)
        """
        if name in self.books:
            # 如果书已经存在，就增加库存
            self.books[name].stock += stock
        else:
            self.books[name] = Book(name, price, stock)

    def find_book(self, name):
        """
        按书名查找
        找到了返回 Book 对象，找不到返回 None
        """
        return self.books.get(name, None)

    def list_available_books(self):
        """列出所有有库存的书"""
        return [book for book in self.books.values() if book.is_available()]

    def get_book_count(self):
        """书店里一共有多少种书"""
        return len(self.books)
