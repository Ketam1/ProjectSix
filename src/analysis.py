from collections import Counter
from datetime import datetime, timedelta
import re
from .constants import LANGUAGE_CONNECTORS, INSULT_WORDS, LOVE_WORDS, SPECIAL_DATES

class Analyzer:
    def __init__(self, messages, conversation_id):
        self.messages = messages
        self.conversation_id = conversation_id

    # Implementing individual functions for each statistic:

    @staticmethod
    def write_to_file(data, file_name):
        with open(file_name, 'w', encoding='utf-8') as file:
            for key, value in data.items():
                file.write(f"{key}\t{value}\n")
        return file_name
    
    def total_messages(self):
        """Returns the total number of messages in the conversation."""
        return len(self.messages)

    def messages_by_sender(self):
        """Counts messages sent by you and by the other participant."""
        from_me_count = sum(1 for message in self.messages if message.from_me)
        from_them_count = len(self.messages) - from_me_count
        return {"from_me": from_me_count, "from_them": from_them_count}

    def average_messages_per_day(self):
        """Calculates the average number of messages sent per day for general, you, and your partner."""
        if not self.messages:
            return {"general": 0, "me": 0, "them": 0}

        start_date = datetime.fromtimestamp(self.messages[0].timestamp / 1000)
        end_date = datetime.fromtimestamp(self.messages[-1].timestamp / 1000)
        days = (end_date - start_date).days or 1

        total_messages = len(self.messages)
        my_messages = sum(1 for message in self.messages if message.from_me)
        their_messages = total_messages - my_messages

        avg_general = total_messages / days
        avg_me = my_messages / days
        avg_them = their_messages / days

        return {
            "average_messages_per_day_general": avg_general,
            "average_messages_per_day_me": avg_me,
            "average_messages_per_day_them": avg_them
        }

    def day_with_most_messages(self):
        """Finds the day on which the most messages were sent."""
        day_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d') for message in self.messages)
        most_common_day = day_counts.most_common(1)
        return most_common_day[0] if most_common_day else None

    def day_with_least_messages(self):
        """Finds the day on which the least messages were sent, excluding days with 0 or 2 messages."""
        day_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d') for message in self.messages)
        
        # Filter out days with 0 or 2 messages
        filtered_day_counts = {day: count for day, count in day_counts.items() if count not in [0, 2]}

        # Find the day with the least number of messages
        if filtered_day_counts:
            least_common_day = min(filtered_day_counts, key=filtered_day_counts.get)
            return (least_common_day, filtered_day_counts[least_common_day])
        else:
            return None

    def most_common_words(self, num_words=30):
        """Identifies the most common words used in the conversation."""
        words = re.findall(r'\w+', ' '.join(message.text_data.lower() for message in self.messages if message.text_data))
        filtered_words = [word for word in words if word not in LANGUAGE_CONNECTORS]
        common_words = Counter(filtered_words).most_common(num_words)

        # Prepare data for writing to file
        common_words_data = {word: count for word, count in common_words}

        file_name = f"most-common-words-{self.conversation_id}.txt"
        Analyzer.write_to_file(common_words_data, file_name)
        return file_name

    def total_words_sent(self):
        """Total number of words sent in the conversation."""
        return sum(len(re.findall(r'\w+', message.text_data)) for message in self.messages if message.text_data)

    def messages_per_hour(self):
        """Number of messages sent per hour."""
        hours = [datetime.fromtimestamp(message.timestamp / 1000).hour for message in self.messages]
        hour_counts = Counter(hours)

        # Preparing the data for writing to file
        hour_counts_data = {f"{hour}:00": count for hour, count in hour_counts.items()}

        file_name = f"messages-per-hour-{self.conversation_id}.txt"
        Analyzer.write_to_file(hour_counts_data, file_name)
        return file_name

    def number_of_emojis(self):
        """Total number of emojis used in the conversation."""
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        return sum(len(emoji_pattern.findall(message.text_data)) for message in self.messages if message.text_data)

    def most_used_emojis(self, top_n=15):
        """Returns a dictionary of the top 'n' most frequently used emojis and their counts."""
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        emojis = [emoji for message in self.messages if message.text_data for emoji in emoji_pattern.findall(message.text_data)]
        top_emojis = Counter(emojis).most_common(top_n)

        # Preparing the data for writing to file
        top_emojis_data = {emoji: count for emoji, count in top_emojis}

        file_name = f"top-emojis-{self.conversation_id}.txt"
        Analyzer.write_to_file(top_emojis_data, file_name)
        return file_name

    def photo_messages_count(self):
        """Number of photos shared in the conversation."""
        return sum(1 for message in self.messages if message.message_type == 1 or message.message_type == 42)

    def sticker_messages_count(self):
        """Number of stickers shared in the conversation."""
        return sum(1 for message in self.messages if message.message_type == 20)
    
    def audio_messages_count(self):
        """Number of audio messages shared."""
        return sum(1 for message in self.messages if message.message_type == 2)

    def video_messages_count(self):
        """Number of videos shared."""
        return sum(1 for message in self.messages if message.message_type == 3)

    def call_count(self):
        """Number of whatsapp calls made."""
        return sum(1 for message in self.messages if message.message_type == 90)
    
    def location_shared_count(self):
        """Number of times location was shared."""
        return sum(1 for message in self.messages if message.message_type == 5 or message.message_type == 16)
    
    def good_morning_night_messages(self):
        """Frequency of various forms of 'Bom dia' and 'Boa noite' messages, including shorthands."""
        morning_pattern = re.compile(r'\b(Bom dia[a-z]*|bd)\b', re.IGNORECASE)
        night_pattern = re.compile(r'\b(Boa noite[a-z]*|bn)\b', re.IGNORECASE)

        morning_count = sum(bool(morning_pattern.search(message.text_data)) for message in self.messages if message.text_data)
        night_count = sum(bool(night_pattern.search(message.text_data)) for message in self.messages if message.text_data)

        return {"bom_dia": morning_count, "boa_noite": night_count}

    def average_response_time(self):
        """Calculate the average response time between messages for general, you, and your partner."""
        response_times = []
        my_response_times = []
        their_response_times = []
        last_message = None

        for message in self.messages:
            if last_message is not None:
                response_time = (message.timestamp - last_message.timestamp) / 1000  # Convert to seconds
                response_times.append(response_time)

                if message.from_me:
                    my_response_times.append(response_time)
                else:
                    their_response_times.append(response_time)

            last_message = message

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        avg_my_response_time = sum(my_response_times) / len(my_response_times) if my_response_times else 0
        avg_their_response_time = sum(their_response_times) / len(their_response_times) if their_response_times else 0

        return {
            "average_response_time_general": avg_response_time,
            "average_response_time_me": avg_my_response_time,
            "average_response_time_them": avg_their_response_time
        }

    def love_words_count(self):
        """Number of messages expressing love."""
        love_word_counts = Counter()
        for message in self.messages:
            if message.text_data:
                words = message.text_data.lower().split()
                for word in words:
                    if word in LOVE_WORDS:
                        love_word_counts[word] += 1

        file_name = f"love-word-counts-{self.conversation_id}.txt"
        Analyzer.write_to_file(dict(love_word_counts), file_name)
        return file_name

    def insult_words_count(self):
        """Number of messages with insult words."""
        insult_word_counts = Counter()
        for message in self.messages:
            if message.text_data:
                words = message.text_data.lower().split()
                for word in words:
                    if word in INSULT_WORDS:
                        insult_word_counts[word] += 1
        file_name = f"insult-word-counts-{self.conversation_id}.txt"
        Analyzer.write_to_file(dict(insult_word_counts), file_name)
        return file_name

    def weekday_frequency_variation(self):
        """Analyze how message count varies by days of the week."""
        weekday_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%A') for message in self.messages)
        file_name = f"weekday-frequency-{self.conversation_id}.txt"
        Analyzer.write_to_file(weekday_counts, file_name)
        return file_name

    def monthly_frequency_variation(self):
        """Analyze how message count varies each month."""
        monthly_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m') for message in self.messages)
        file_name = f"monthly-frequency-{self.conversation_id}.txt"
        Analyzer.write_to_file(monthly_counts, file_name)
        return file_name

    def daily_frequency_variation(self):
        """Analyze how message count varies each day."""
        daily_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d') for message in self.messages)
        file_name = f"daily-frequency-{self.conversation_id}.txt"
        Analyzer.write_to_file(daily_counts, file_name)
        return file_name

    def analyze(self):
        return {
            "Total Messages": self.total_messages(),
            "Messages by Sender": self.messages_by_sender(),
            "Average Messages per Day": self.average_messages_per_day(),
            "Day with Most Messages": self.day_with_most_messages(),
            "Day with Least Messages": self.day_with_least_messages(),
            "Most Common Words": self.most_common_words(),
            "Total Words Sent": self.total_words_sent(),
            "Messages per Hour": self.messages_per_hour(),
            "Number of Emojis": self.number_of_emojis(),
            "Most Used Emoji": self.most_used_emojis(),
            "Photo Messages Count": self.photo_messages_count(),
            "Sticker Messages Count": self.sticker_messages_count(),
            "Video Messages Count": self.video_messages_count(),
            "Audio Messages Count": self.audio_messages_count(),
            "Location Messages Count": self.location_shared_count(),
            "Call Count": self.call_count(),
            "Good Morning/Night Messages": self.good_morning_night_messages(),
            "Average Response Time": self.average_response_time(),
            "Love Words Count": self.love_words_count(),
            "Insult Words Count": self.insult_words_count(),
            "Monthly Message Frequency Variation": self.monthly_frequency_variation(),
            "Daily Message Frequency Variation": self.daily_frequency_variation(),
            "Weekday Message Frequency Variation": self.weekday_frequency_variation(),
        }
        