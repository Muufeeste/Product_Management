import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap, QFont
from PyQt5.QtCore import Qt
import sqlite3
import style

# Use your DB file
con = sqlite3.connect("products.db", check_same_thread=False)
cur = con.cursor()

defaultImg = "store.png"


class SellProducts(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sell Products")
        self.setWindowIcon(QIcon('icons/icon.ico'))
        self.setGeometry(450, 150, 350, 600)
        self.setFixedSize(self.size())

        self.UI()
        self.show()

    def UI(self):
        self.widgets()
        self.layouts()

    def widgets(self):
        # Top
        self.sellProductImg = QLabel()
        self.img = QPixmap('icons/shop.png')
        self.sellProductImg.setPixmap(self.img)
        self.sellProductImg.setAlignment(Qt.AlignCenter)

        self.titleText = QLabel("Sell Products")
        self.titleText.setAlignment(Qt.AlignCenter)

        # Bottom
        self.productCombo = QComboBox()
        self.memberCombo = QComboBox()
        self.quantityCombo = QComboBox()

        self.submitBtn = QPushButton("Submit")
        self.submitBtn.clicked.connect(self.sellProduct)

        # Load data
        query_products = "SELECT product_id, product_name, product_quota FROM products WHERE product_availability=?"
        products = cur.execute(query_products, ('Available',)).fetchall()

        query_members = "SELECT member_id, member_name FROM members"
        members = cur.execute(query_members).fetchall()

        # Fill combos
        self.productCombo.blockSignals(True)
        self.productCombo.clear()

        for pid, pname, pquota in products:
            self.productCombo.addItem(pname, pid)

        self.productCombo.blockSignals(False)
        self.productCombo.currentIndexChanged.connect(self.changeComboValue)

        self.memberCombo.clear()
        for mid, mname in members:
            self.memberCombo.addItem(mname, mid)

        # Handle no available products
        if not products:
            QMessageBox.information(self, "Info", "No available products to sell.")
            self.submitBtn.setEnabled(False)
            return

        # Initialize quantity based on first product
        first_quota = products[0][2]  # product_quota
        self.populate_quantity(first_quota)

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.topLayout = QVBoxLayout()
        self.bottomLayout = QFormLayout()

        self.topFrame = QFrame()
        self.topFrame.setStyleSheet(style.sellProductTopFrame())

        self.bottomFrame = QFrame()
        self.bottomFrame.setStyleSheet(style.sellProductBottomFrame())

        self.topLayout.addWidget(self.titleText)
        self.topLayout.addWidget(self.sellProductImg)
        self.topFrame.setLayout(self.topLayout)

        self.bottomLayout.addRow(QLabel("Product: "), self.productCombo)
        self.bottomLayout.addRow(QLabel("Member: "), self.memberCombo)
        self.bottomLayout.addRow(QLabel("Quantity: "), self.quantityCombo)
        self.bottomLayout.addRow(QLabel(""), self.submitBtn)
        self.bottomFrame.setLayout(self.bottomLayout)

        self.mainLayout.addWidget(self.topFrame)
        self.mainLayout.addWidget(self.bottomFrame)
        self.setLayout(self.mainLayout)

    # --- Helpers ---
    def clear_quantity(self):
        self.quantityCombo.blockSignals(True)
        self.quantityCombo.clear()
        self.quantityCombo.blockSignals(False)

    def populate_quantity(self, quota: int):
        self.clear_quantity()

        if quota is None or quota <= 0:
            self.quantityCombo.addItem("0")
            self.submitBtn.setEnabled(False)
            return

        self.submitBtn.setEnabled(True)
        for i in range(1, quota + 1):
            self.quantityCombo.addItem(str(i))

    # --- Events ---
    def changeComboValue(self):
        product_id = self.productCombo.currentData()
        if product_id is None:
            return

        query = "SELECT product_quota FROM products WHERE product_id=?"
        row = cur.execute(query, (product_id,)).fetchone()
        if not row:
            self.populate_quantity(0)
            return

        quota = row[0]
        self.populate_quantity(quota)

    def sellProduct(self):
        # Make sure quantity is valid
        if self.quantityCombo.currentText() in ("", "0"):
            QMessageBox.information(self, "Info", "Quantity must be at least 1.")
            return

        productName = self.productCombo.currentText()
        productId = self.productCombo.currentData()
        memberName = self.memberCombo.currentText()
        memberId = self.memberCombo.currentData()
        quantity = int(self.quantityCombo.currentText())

        self.confirm = ConfirmWindow(productName, productId, memberName, memberId, quantity)
        self.confirm.show()
        self.close()


class ConfirmWindow(QWidget):
    def __init__(self, productName, productId, memberName, memberId, quantity):
        super().__init__()
        self.setWindowTitle("Sell Product")
        self.setWindowIcon(QIcon("icons/icon.ico"))
        self.setGeometry(450, 150, 350, 600)
        self.setFixedSize(self.size())

        self.productNameValue = productName
        self.productId = productId
        self.memberNameValue = memberName
        self.memberId = memberId
        self.quantity = quantity

        self.UI()
        self.show()

    def UI(self):
        self.widgets()
        self.layouts()

    def widgets(self):
        # Top
        self.sellProductImg = QLabel()
        self.img = QPixmap('icons/shop.png')
        self.sellProductImg.setPixmap(self.img)
        self.sellProductImg.setAlignment(Qt.AlignCenter)

        self.titleText = QLabel("Sell Product")
        self.titleText.setAlignment(Qt.AlignCenter)

        # Price
        priceQuery = "SELECT product_price FROM products WHERE product_id=?"
        price_row = cur.execute(priceQuery, (self.productId,)).fetchone()
        if not price_row:
            QMessageBox.information(self, "Info", "Product not found.")
            self.close()
            return

        self.price = price_row[0]
        self.amount = self.quantity * self.price

        # Bottom labels
        self.productName = QLabel(self.productNameValue)
        self.memberName = QLabel(self.memberNameValue)

        self.amountLabel = QLabel(f"{self.price} x {self.quantity} = {self.amount}")

        self.confirmBtn = QPushButton("Confirm")
        self.confirmBtn.clicked.connect(self.confirm)

    def layouts(self):
        self.mainLayout = QVBoxLayout()
        self.topLayout = QVBoxLayout()
        self.bottomLayout = QFormLayout()

        self.topFrame = QFrame()
        self.topFrame.setStyleSheet(style.confirmProductTopFrame())

        self.bottomFrame = QFrame()
        self.bottomFrame.setStyleSheet(style.confirmProductBottomFrame())

        self.topLayout.addWidget(self.titleText)
        self.topLayout.addWidget(self.sellProductImg)
        self.topFrame.setLayout(self.topLayout)

        self.bottomLayout.addRow(QLabel("Product: "), self.productName)
        self.bottomLayout.addRow(QLabel("Member: "), self.memberName)
        self.bottomLayout.addRow(QLabel("Amount: "), self.amountLabel)
        self.bottomLayout.addRow(QLabel(""), self.confirmBtn)

        self.bottomFrame.setLayout(self.bottomLayout)

        self.mainLayout.addWidget(self.topFrame)
        self.mainLayout.addWidget(self.bottomFrame)
        self.setLayout(self.mainLayout)

    def confirm(self):
        try:
            # Insert selling row
            sellQuery = """
                INSERT INTO sellings (selling_product_id, selling_member_id, selling_quantity, selling_amount)
                VALUES (?, ?, ?, ?)
            """
            cur.execute(sellQuery, (self.productId, self.memberId, self.quantity, self.amount))

            # Read current quota
            qQuery = "SELECT product_quota FROM products WHERE product_id=?"
            row = cur.execute(qQuery, (self.productId,)).fetchone()
            if not row:
                con.rollback()
                QMessageBox.information(self, "Info", "Product not found.")
                return

            current_quota = row[0]
            new_quota = current_quota - self.quantity

            if new_quota <= 0:
                updateQuery = "UPDATE products SET product_quota=?, product_availability=? WHERE product_id=?"
                cur.execute(updateQuery, (0, 'UnAvailable', self.productId))
            else:
                updateQuery = "UPDATE products SET product_quota=? WHERE product_id=?"
                cur.execute(updateQuery, (new_quota, self.productId))

            con.commit()
            QMessageBox.information(self, "Info", "Success")
            self.close()

        except Exception as e:
            con.rollback()
            print("SELL ERROR:", e)
            QMessageBox.information(self, "Info", "Something went wrong!")
