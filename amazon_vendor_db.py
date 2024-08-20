import pyodbc
from config import create_connection_string, db_config
from datetime import datetime
import getpass
import socket


class AmazonVendorDb:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Establish a new connection to the database."""
        self.conn = pyodbc.connect(create_connection_string(db_config["AmazonVendor"]))
        self.cursor = self.conn.cursor()

    def check_if_connected(self):
        """Check if the database connection is active."""
        try:
            self.cursor.execute("SELECT 1")
            return True
        except (pyodbc.ProgrammingError, pyodbc.OperationalError):
            return False

    def reconnect(self):
        """Reconnect to the database if the connection is lost."""
        if not self.check_if_connected():
            self.connect()

    def has_tracking_been_checked_in(self, tracking_number):
        """Check if a tracking number has already been checked in."""
        self.cursor.execute(
            """
            SELECT item_id FROM ReturnShipments WHERE tracking_number = ?
            """,
            tracking_number,
        )
        item_id = self.cursor.fetchone()[0]

        return item_id

    def get_received_order_count(self, authorization_id):
        """Get the number of items received for a return authorization."""
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM returnshipments WHERE authorization_id = (SELECT id FROM ReturnAuthorizations WHERE amz_authorization_id = ?) AND received = 1
            """,
            authorization_id,
        )
        count = self.cursor.fetchone()[0]

        return count

    def search_tracking_number(self, tracking_number):
        """Search for a tracking number in the database."""

        self.cursor.execute(
            """
            SELECT id, amz_authorization_id FROM ReturnAuthorizations 
            WHERE id = (SELECT authorization_id FROM ReturnShipments WHERE tracking_number = ?)
            """,
            tracking_number,
        )
        result = self.cursor.fetchone()

        # The tracking number is not in the database
        if not result:
            return None, None, None, None, None, None

        authorization_id, authorization_number = result

        self.cursor.execute(
            """
            SELECT tracking_number, received, item_id FROM ReturnShipments WHERE authorization_id = ?
            """,
            authorization_id,
        )
        shipments_rows = {
            row.tracking_number: {
                "received": row.received,
                "item_id": row.item_id,
            }
            for row in self.cursor.fetchall()
        }

        self.cursor.execute(
            """
            SELECT id, sku, status, note FROM ReturnItems WHERE authorization_id = ?
            """,
            authorization_id,
        )
        items_rows = {
            row.id: {"sku": row.sku, "status": row.status, "note": row.note}
            for row in self.cursor.fetchall()
        }

        # Find the amount od skus expected to be received
        sku_amount_received = 0
        expected_sku_amount = len(items_rows)
        for key in shipments_rows:
            if shipments_rows[key]["received"]:
                sku_amount_received += 1

        # If the item has already been received
        if shipments_rows[tracking_number]["received"]:
            item_id = shipments_rows[tracking_number]["item_id"]
            skus = [items_rows[item_id]["sku"]]
            notes = {items_rows[item_id]["sku"]: items_rows[item_id]["note"]}
            item_status = items_rows[item_id]["status"]

            return (
                skus,
                authorization_number,
                expected_sku_amount,
                sku_amount_received,
                item_status,
                notes,
            )
        else:
            # Removing received skus of the list
            item_ids = [
                shipments_rows[key]["item_id"]
                for key in shipments_rows
                if shipments_rows[key]["received"]
            ]
            skus = [items_rows[key]["sku"] for key in items_rows if key not in item_ids]
            notes = {}
            item_status = ""
            return (
                skus,
                authorization_number,
                expected_sku_amount,
                sku_amount_received,
                item_status,
                notes,
            )

    # def get_checked_in_skus(self, item_id):
    #     self.cursor.execute(
    #         """
    #         SELECT sku, note FROM ReturnItems ri
    #         JOIN ReturnShipments rs ON ri.authorization_id = rs.authorization_id
    #         WHERE ri.id = ?

    #         """,
    #         item_id,
    #     )
    #     rows = self.cursor.fetchall()
    #     skus = [rows[0].sku]
    #     notes = {rows[0].sku: rows[0].note}
    #     return skus, notes

    # def insert_custom_return_item(self, authorization_id, sku):
    #     """Insert a custom return item into the database."""
    #     filler = "Custom Return"
    #     self.cursor.execute(
    #         """
    #         INSERT INTO ReturnItems (
    #             authorization_id,
    #             po_date,
    #             sku,
    #             po_number,
    #             requested_qty,
    #             approved_qty,
    #             requested_refund_per_unit,
    #             approved_refund_per_unit,
    #             vendor_code,
    #             warehouse_code,
    #             request_id,
    #             request_item_id,
    #             external_id)
    #         VALUES ((SELECT id FROM ReturnAuthorizations WHERE amz_authorization_id = ?), ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #         """,
    #         authorization_id,
    #         datetime.now().strftime("%Y-%m-%d"),
    #         sku,
    #         filler,
    #         1,
    #         1,
    #         0.0,
    #         0.0,
    #         "N/A",
    #         "N/A",
    #         filler,
    #         filler,
    #         filler,
    #     )
    #     self.conn.commit()

    def check_in_return(self, authorization_id, tracking_number, sku, status, note):
        """Check in a return to the database."""

        # sku_split = sku.split(" ")
        # sku_split[0] = sku_split[0].upper()

        # if len(sku_split) > 1:
        #     if sku_split[1] == "(Other)":
        #         sku = sku_split[0]
        #         count = self.verify_sku(sku)
        #         if count == 0:
        #             return "sku not found"
        #         else:
        #             self.insert_custom_return_item(
        #                 authorization_id, sku_split[0]
        #             )
        #     elif sku_split[1] == "(Continue)":
        #         sku = sku_split[0]
        #         self.insert_custom_return_item(
        #             authorization_id, sku_split[0], status, note
        #         )

        try:
            self.cursor.execute(
                """
                UPDATE ReturnItems SET status = ?, note = ? WHERE sku = ? and authorization_id = (SELECT id FROM ReturnAuthorizations WHERE amz_authorization_id = ?)
                """,
                status,
                note,
                sku,
                authorization_id,
            )

            item_id = self.get_item_id(authorization_id, sku)
            username = getpass.getuser()
            hostname = socket.gethostname()

            self.cursor.execute(
                """
                UPDATE ReturnShipments SET received = 1, received_date = ?, item_id = ?, logged_user = ?, station = ? WHERE tracking_number = ?
                """,
                datetime.now(),
                item_id,
                username,
                hostname,
                tracking_number,
            )

            self.conn.commit()

        except pyodbc.IntegrityError:
            return "error checking in return"

    def get_item_id(self, authorization_id, sku):
        """Get the item ID of a return item."""
        self.cursor.execute(
            """
            SELECT id FROM ReturnItems WHERE authorization_id = (SELECT id FROM ReturnAuthorizations WHERE amz_authorization_id = ?) AND sku = ?
            """,
            authorization_id,
            sku,
        )
        item_id = self.cursor.fetchone()[0]

        return item_id

    def verify_sku(self, sku):
        """Verify if a SKU is in the database."""
        self.cursor.execute(
            """
            SELECT COUNT(*) FROM vProductAndAliasDetailsView WHERE sku = ?
            """,
            sku,
        )
        count = self.cursor.fetchone()[0]

        return count

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
            self.cursor = None
