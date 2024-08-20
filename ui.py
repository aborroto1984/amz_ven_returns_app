from PyQt5.QtWidgets import (
    QMainWindow,
    QLabel,
    QLineEdit,
    QPushButton,
    QComboBox,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QSizePolicy,
    QMessageBox,
    QDesktopWidget,
)
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt
from amazon_vendor_db import AmazonVendorDb
import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Global varibles
        self.current_notes = {}
        self.db = AmazonVendorDb()

        self.setWindowIcon(QIcon(resource_path("AVRC.ico")))
        self.setWindowTitle("Amazon Vendor Returns Check-In")

        # Create the main horizontal layo
        main_layout = QVBoxLayout()
        main_layout.setSpacing(30)
        main_layout.setContentsMargins(40, 40, 40, 40)

        # Header section-----------------------------------------
        # Create box layout for header section
        header_layout = QHBoxLayout()
        header_layout.setSpacing(5)

        # Create a label for sucessful check-in
        self.check_in_label = QLabel()
        # self.check_in_label.setMinimumHeight(self.check_in_label.fontMetrics().height())
        self.check_in_label.setText(" ")
        self.check_in_label.setAlignment(Qt.AlignLeft)
        check_in_label_color = "color: green"  # Green text color
        self.check_in_label.setStyleSheet(check_in_label_color)
        header_layout.addWidget(self.check_in_label)

        # Create a label for the database connection status
        self.db_label = QLabel("Connected to Database")
        db_label_color = "color: green"  # Green text color
        self.db_label.setStyleSheet(db_label_color)
        self.db_label.setAlignment(Qt.AlignRight)
        header_layout.addWidget(self.db_label)

        # Add the header layout to the main layout
        main_layout.addLayout(header_layout)

        # Tracking number section----------------------------------------------
        # Create box layout for tracking number section
        tracking_layout = QVBoxLayout()
        tracking_layout.setSpacing(5)

        # Create a label for tracking number
        self.tracking_label = QLabel("Tracking Number:")
        self.tracking_label.setAlignment(Qt.AlignLeft)
        tracking_layout.addWidget(self.tracking_label)

        # Create a large text field for tracking number
        self.tracking_number_field = QLineEdit()
        self.tracking_font = QFont("Arial", 26, QFont.Bold)
        self.tracking_number_field.setFont(self.tracking_font)
        self.tracking_number_field.setPlaceholderText("Enter Tracking Number")
        self.tracking_number_field.setMinimumHeight(70)  # Make the text field larger
        self.tracking_number_field.setMinimumWidth(600)  # Adjust width as needed
        self.tracking_number_field.returnPressed.connect(self.search_tracking_number)
        tracking_layout.addWidget(self.tracking_number_field)

        # Add the tracking layout to the main layout
        main_layout.addLayout(tracking_layout)

        # Drop Box section-----------------------------------------------------
        # Create verticcal layout for the sku dropdown and its label
        self.sku_layout = QVBoxLayout()
        self.sku_layout.setSpacing(10)

        # Create a label for SKU selection
        self.sku_label = QLabel("Select SKU:")
        self.sku_label.setAlignment(Qt.AlignLeft)
        self.sku_layout.addWidget(self.sku_label)

        # Create a dropdown menu for SKU selection
        self.sku_dropdown = QComboBox()
        self.sku_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.sku_dropdown.setMinimumHeight(40)
        self.sku_dropdown.currentIndexChanged.connect(self.on_sku_change)
        self.sku_layout.addWidget(self.sku_dropdown)

        # Create vertical layout for the status dropdown and its label
        self.status_layout = QVBoxLayout()
        self.status_layout.setSpacing(10)

        # Create a label for status selection
        self.status_label = QLabel("Select Status:")
        self.status_label.setAlignment(Qt.AlignLeft)
        self.status_layout.addWidget(self.status_label)

        # Create a dropdown menu for status selection
        self.status_dropdown = QComboBox()
        self.status_dropdown.addItems(["Complete", "Incomplete", "Damaged"])
        self.status_dropdown.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.status_dropdown.setMinimumHeight(40)
        self.status_layout.addWidget(self.status_dropdown)

        # Create horizontal layout for the dropdowns
        self.dropdown_layout = QHBoxLayout()
        self.dropdown_layout.addLayout(self.sku_layout)
        self.dropdown_layout.addLayout(self.status_layout)

        # Add the dropdown layout to the main layout
        main_layout.addLayout(self.dropdown_layout)

        # Note section-------------------------------------------------------
        # Create vertical layout for the note section
        self.note_layout = QVBoxLayout()
        self.note_layout.setSpacing(10)

        # Create a label for the note
        self.note_label = QLabel("Note:")
        self.note_label.setAlignment(Qt.AlignLeft)

        # Create a text field for the note
        self.note_field = QLineEdit()
        self.note_field.setPlaceholderText("Enter Note")
        self.note_field.setMinimumHeight(40)  # Standard text field size
        self.note_layout.addWidget(self.note_label)
        self.note_layout.addWidget(self.note_field)

        # Create vertical layout for other sku section
        self.other_sku_layout = QVBoxLayout()
        self.other_sku_layout.setSpacing(10)

        # # Create a label for other sku
        # self.other_sku_label = QLabel("Other Sku:")
        # self.other_sku_label.setAlignment(Qt.AlignLeft)

        # # Create a text field for other sku
        # self.other_sku_field = QLineEdit()
        # self.other_sku_field.setPlaceholderText("Enter Other Sku")
        # self.other_sku_field.setMinimumHeight(40)  # Standard text field size
        # self.other_sku_field.setDisabled(True)
        # self.other_sku_layout.addWidget(self.other_sku_label)
        # self.other_sku_layout.addWidget(self.other_sku_field)

        # Create horizontal layout for the note and other sku
        self.note_other_sku_layout = QHBoxLayout()
        self.note_other_sku_layout.addLayout(self.other_sku_layout)
        self.note_other_sku_layout.addLayout(self.note_layout)

        # Add the note layout to the main layout
        main_layout.addLayout(self.note_other_sku_layout)

        # Information section------------------------------------------------
        # Create vertical layout for the information section desciptions
        self.info_labels_layout = QVBoxLayout()
        self.info_labels_layout.setSpacing(5)

        # Create a label for the information section description
        self.auth_label = QLabel("Authorization ID:")
        self.auth_label.setAlignment(Qt.AlignLeft)

        self.expected_label = QLabel("Expected Number of Skus:")
        self.expected_label.setAlignment(Qt.AlignLeft)

        self.received_label = QLabel("Received Number of Skus:")
        self.received_label.setAlignment(Qt.AlignLeft)

        # Add the information section descriptions to the layout
        self.info_labels_layout.addWidget(self.auth_label)
        self.info_labels_layout.addWidget(self.expected_label)
        self.info_labels_layout.addWidget(self.received_label)

        # Create vertical layout for the information section values
        self.info_values_layout = QVBoxLayout()
        self.info_values_layout.setSpacing(5)

        # Create labels for the information values
        self.auth_value = QLabel(" ")
        self.auth_value.setAlignment(Qt.AlignRight)

        self.expected_value = QLabel(" ")
        self.expected_value.setAlignment(Qt.AlignRight)

        self.received_value = QLabel(" ")
        self.received_value.setAlignment(Qt.AlignRight)

        # Add the information section values to the layout
        self.info_values_layout.addWidget(self.auth_value)
        self.info_values_layout.addWidget(self.expected_value)
        self.info_values_layout.addWidget(self.received_value)

        # Create horizontal layout for the information section
        self.info_layout = QHBoxLayout()
        self.info_layout.addLayout(self.info_labels_layout)
        self.info_layout.addLayout(self.info_values_layout)

        # Add the information section layout to the main layout
        main_layout.addLayout(self.info_layout)

        # Button section-----------------------------------------------------
        # Create a button
        self.submit_button = QPushButton("Check In Return")
        self.submit_button.setFixedSize(250, 50)  # Fixed size for the button
        self.submit_button.clicked.connect(self.on_check_in)

        # Create a layout just for the button to center it
        self.button_layout = QHBoxLayout()
        self.button_layout.setContentsMargins(0, 0, 0, 20)
        self.button_layout.addStretch()  # Add stretchable space before the button
        self.button_layout.addWidget(self.submit_button)
        self.button_layout.addStretch()  # Add stretchable space after the button

        # Add the button layout to the main layout
        main_layout.addLayout(self.button_layout)

        # Set the layout to a central widget
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Center the window
        self.center()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.focusWidget() != self.tracking_number_field:
                self.submit_button.click()
        #     else:
        #         super().keyPressEvent(event)  # Pass the event to the base class if needed
        # else:
        #     super().keyPressEvent(event)  # Pass other key events to the base class

    def on_sku_change(self):
        sku = self.sku_dropdown.currentText()
        if sku == "Other":
            self.other_sku_field.setDisabled(False)
            self.other_sku_field.setFocus()
        else:
            self.other_sku_field.clear()
            self.other_sku_field.setDisabled(True)

        if sku in self.current_notes:
            self.note_field.setText(self.current_notes[sku])
        else:
            self.note_field.setText("")

    def search_tracking_number(self):
        self.reset_fields(clear_tracking=False)
        tracking_number = self.tracking_number_field.text()
        if self.check_db_connection():
            (
                skus,
                authorization_id,
                expected_sku_amount,
                sku_amount_received,
                item_status,
                self.current_notes,
            ) = self.db.search_tracking_number(tracking_number)

            if not skus or not authorization_id or not expected_sku_amount:
                self.check_in_label.setStyleSheet("color: red")
                self.check_in_label.setText("Tracking Number not found.")
                return

            if item_status:
                self.status_dropdown.setCurrentText(item_status)

            self.check_in_label.setText(" ")
            # Adding Other SKU to the dropdown
            skus.append("Other")
            self.sku_dropdown.addItems(skus)
            self.auth_value.setText(authorization_id)
            self.expected_value.setText(str(expected_sku_amount))
            self.received_value.setText(
                f"{sku_amount_received} out of {expected_sku_amount}"
            )
            if skus[0] in self.current_notes:
                self.note_field.setText(self.current_notes[skus[0]])
            else:
                self.note_field.setText("")

    def on_check_in(self):
        if self.check_db_connection():
            tracking_number = self.tracking_number_field.text()
            if not tracking_number:
                self.check_in_label.setStyleSheet("color: red")
                self.check_in_label.setText("Tracking Number cannot be empty.")
            sku = self.sku_dropdown.currentText()
            # if sku == "Other":
            #     sku = self.other_sku_field.text() + " (Other)"
            status = self.status_dropdown.currentText()
            note = self.note_field.text()
            authorization_id = self.auth_value.text()

            error_message = self.db.check_in_return(
                authorization_id, tracking_number, sku, status, note
            )
            # if error_message == "sku not found":
            #     if self.show_sku_not_found_message(sku):
            #         sku = self.other_sku_field.text() + " (Continue)"
            #         self.db.check_in_return(
            #             authorization_id, tracking_number, sku, status, note
            #         )
            #     else:
            #         self.reset_fields()
            #         return
            # elif error_message == "error checking in return":
            #     self.show_error_message()
            #     self.reset_fields()
            #     return

            self.reset_fields()
            self.check_in_label.setStyleSheet("color: green")
            self.check_in_label.setText("Check In Successfull")
        else:
            self.check_in_label.setStyleSheet("color: red")
            self.check_in_label.setText("Failed to Check In")

    def reset_fields(self, clear_tracking=True):
        if clear_tracking:
            self.tracking_number_field.clear()
        self.sku_dropdown.clear()
        self.status_dropdown.setCurrentIndex(0)
        self.note_field.clear()
        self.auth_value.setText(" ")
        self.expected_value.setText(" ")
        self.received_value.setText(" ")
        self.current_notes = {}
        self.sku_dropdown.clear()
        self.other_sku_field.clear()
        self.other_sku_field.setDisabled(True)
        self.tracking_number_field.setFocus()

    def check_db_connection(self):
        if self.db.check_if_connected():
            self.db_label.setText("Connected to Database")
            self.db_label.setStyleSheet("color: green")
            return True
        else:
            try:
                self.db.reconnect()
                self.db_label.setText("Connected to Database")
                self.db_label.setStyleSheet("color: green")
                return True
            except Exception as e:
                self.db_label.setText("Disconnected from Database")
                self.db_label.setStyleSheet("color: red")
                return False

    # def show_sku_not_found_message(self, sku):
    #     message = QMessageBox()
    #     message.setWindowTitle("SKU Not Found")
    #     message.setText(
    #         f"The SKU: {sku} was not found.\nWould you like to continue anyways?"
    #     )
    #     message.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    #     message.setIcon(QMessageBox.Warning)
    #     message.adjustSize()
    #     message.setContentsMargins(20, 20, 20, 20)
    #     message.setDefaultButton(QMessageBox.No)
    #     message.setEscapeButton(QMessageBox.No)
    #     self.center_on_screen(message)
    #     message.exec_()

    #     if message.clickedButton() == QMessageBox.Yes:
    #         return True
    #     else:
    #         return False

    # def show_error_message(self):
    #     message = QMessageBox()
    #     message.setWindowTitle("Error")
    #     message.setText(
    #         "An error occured while checking in the return.\nTry again and if the problem persists contact \nthe IT department."
    #     )
    #     message.setStandardButtons(QMessageBox.Ok)
    #     message.setIcon(QMessageBox.Critical)
    #     message.setContentsMargins(20, 20, 20, 20)
    #     message.setDefaultButton(QMessageBox.Ok)
    #     message.setEscapeButton(QMessageBox.Ok)
    #     self.center_on_screen(message)
    #     message.exec_()

    # def center_on_screen(self, dialog):
    #     # Get the screen geometry
    #     screen_geometry = QDesktopWidget().availableGeometry()

    #     # Get the dialog's size
    #     dialog_geometry = self.frameGeometry()

    #     # Calculate the position to move the dialog to the center of the screen
    #     x = (screen_geometry.width() - dialog_geometry.width()) // 2
    #     y = (screen_geometry.height() - dialog_geometry.height()) // 2

    #     # Move the dialog to the calculated position
    #     self.move(x, y)

    def center(self):
        # Get the screen geometry
        screen_geometry = QDesktopWidget().availableGeometry()

        # Get the window geometry
        window_geometry = self.frameGeometry()

        # Calculate the center point
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2

        # Move the window to the calculated position
        self.move(x, y)
