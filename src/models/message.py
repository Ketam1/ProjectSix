class Message:
    def __init__(self, message_id, timestamp, text_data, message_type, from_me):
        self.message_id = message_id
        self.timestamp = timestamp
        self.text_data = text_data
        self.message_type = message_type
        self.from_me = bool(from_me)  # Converts to boolean, 1 = True, 0 = False

    def __str__(self):
        return f"Message ID: {self.message_id}, Timestamp: {self.timestamp}, Text: {self.text_data}, Type: {self.message_type}, From Me: {self.from_me}"

    @staticmethod
    def from_row(row):
        """Create a Message object from a database row."""
        return Message(
            message_id=row[0], 
            timestamp=row[13],  # Assuming 'timestamp' is the 14th column
            text_data=row[17],  # Assuming 'text_data' is the 18th column
            message_type=row[16],  # Assuming 'message_type' is the 17th column
            from_me=row[3]  # Assuming 'from_me' is the 4th column
        )
