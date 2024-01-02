from collections import Counter
from datetime import datetime, timedelta
import re
from .constants import LANGUAGE_CONNECTORS, HAPPY_WORDS, SAD_WORDS, LOVE_WORDS, SPECIAL_DATES

class Analyzer:
    def __init__(self, messages):
        self.messages = messages

    # Implementing individual functions for each statistic:

    def total_messages(self):
        """Returns the total number of messages in the conversation."""
        return len(self.messages)

    def messages_by_sender(self):
        """Counts messages sent by you and by the other participant."""
        from_me_count = sum(1 for message in self.messages if message.from_me)
        from_them_count = len(self.messages) - from_me_count
        return {"from_me": from_me_count, "from_them": from_them_count}

    def average_messages_per_day(self):
        """Calculates the average number of messages sent per day."""
        if not self.messages:
            return 0

        start_date = datetime.fromtimestamp(self.messages[0].timestamp / 1000)
        end_date = datetime.fromtimestamp(self.messages[-1].timestamp / 1000)
        days = (end_date - start_date).days or 1
        return len(self.messages) / days

    def day_with_most_messages(self):
        """Finds the day on which the most messages were sent."""
        day_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d') for message in self.messages)
        most_common_day = day_counts.most_common(1)
        return most_common_day[0] if most_common_day else None

    def most_common_words(self, num_words=30):
        """Identifies the most common words used in the conversation."""
        words = re.findall(r'\w+', ' '.join(message.text_data.lower() for message in self.messages if message.text_data))
        filtered_words = [word for word in words if word not in LANGUAGE_CONNECTORS]
        return Counter(filtered_words).most_common(num_words)

    def total_words_sent(self):
        """Total number of words sent in the conversation."""
        return sum(len(re.findall(r'\w+', message.text_data)) for message in self.messages if message.text_data)

    def average_word_count_per_message(self):
        """Average number of words per message."""
        total_words = self.total_words_sent()
        total_messages = len(self.messages)
        return total_words / total_messages if total_messages else 0

    def messages_per_hour(self):
        """Number of messages sent per hour."""
        hours = [datetime.fromtimestamp(message.timestamp / 1000).hour for message in self.messages]
        return Counter(hours)

    def longest_message(self):
        """The longest message under 1000 characters."""
        if not self.messages:
            return None
        filtered_messages = [message for message in self.messages if message.text_data and len(message.text_data) < 300]
        return max(filtered_messages, key=lambda message: len(message.text_data), default=None)

    def number_of_emojis(self):
        """Total number of emojis used in the conversation."""
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        return sum(len(emoji_pattern.findall(message.text_data)) for message in self.messages if message.text_data)

    def most_used_emojis(self, top_n=15):
        """Returns a dictionary of the top 'n' most frequently used emojis and their counts."""
        emoji_pattern = re.compile("[\U00010000-\U0010ffff]", flags=re.UNICODE)
        emojis = [emoji for message in self.messages if message.text_data for emoji in emoji_pattern.findall(message.text_data)]
        top_emojis = Counter(emojis).most_common(top_n)
        return {emoji: count for emoji, count in top_emojis}

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
    
    def messages_on_special_dates(self):
        """Retorna a contagem de mensagens enviadas em datas especiais definidas em constants.py."""
        # Convertendo as datas do dicionário para o formato apropriado
        special_dates = {datetime.strptime(date_str, '%d-%m-%Y').date(): event for event, date_str in SPECIAL_DATES.items()}
        messages_count = {}

        for date, event in special_dates.items():
            count = sum(datetime.fromtimestamp(message.timestamp / 1000).date() == date for message in self.messages)
            messages_count[event] = count

        return messages_count
    
    def good_morning_night_messages(self):
        """Frequency of various forms of 'Bom dia' and 'Boa noite' messages, including shorthands."""
        morning_pattern = re.compile(r'\b(Bom dia[a-z]*|bd)\b', re.IGNORECASE)
        night_pattern = re.compile(r'\b(Boa noite[a-z]*|bn)\b', re.IGNORECASE)

        morning_count = sum(bool(morning_pattern.search(message.text_data)) for message in self.messages if message.text_data)
        night_count = sum(bool(night_pattern.search(message.text_data)) for message in self.messages if message.text_data)

        return {"bom_dia": morning_count, "boa_noite": night_count}

    def days_without_messages(self):
        """List of specific dates without any messages."""
        if not self.messages:
            return []

        dates_with_messages = {datetime.fromtimestamp(message.timestamp / 1000).date() for message in self.messages}
        start_date = min(dates_with_messages)
        end_date = max(dates_with_messages)

        all_dates = {start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)}
        days_without_messages = all_dates - dates_with_messages

        # Convert set to a sorted list
        return sorted(days_without_messages)

    def average_response_time(self):
        """Calculate the average response time between messages, separately for you and your partner."""
        my_response_times = []
        their_response_times = []
        last_message_from_me = None

        for message in self.messages:
            if last_message_from_me is not None:
                response_time = (message.timestamp - last_message_from_me.timestamp) / 1000  # Convert to seconds
                if message.from_me:
                    my_response_times.append(response_time)
                else:
                    their_response_times.append(response_time)

            if message.from_me:
                last_message_from_me = message

        avg_my_response_time = sum(my_response_times) / len(my_response_times) if my_response_times else 0
        avg_their_response_time = sum(their_response_times) / len(their_response_times) if their_response_times else 0

        return {
            "average_response_time_me": avg_my_response_time,
            "average_response_time_them": avg_their_response_time
        }

    def count_love_messages(self):
        """Number of messages expressing love."""
        return sum(any(word in message.text_data.lower() for word in LOVE_WORDS) for message in self.messages if message.text_data)

    def happy_sad_words_count(self):
        """Number of messages with happy or sad words."""
        happy_count = sum(any(word in message.text_data.lower() for word in HAPPY_WORDS) for message in self.messages if message.text_data)
        sad_count = sum(any(word in message.text_data.lower() for word in SAD_WORDS) for message in self.messages if message.text_data)
        return {'happy': happy_count, 'sad': sad_count}

    def monthly_frequency_variation(self):
        """Analyze how message count varies each month."""
        monthly_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m') for message in self.messages)
        return monthly_counts

    def daily_frequency_variation(self):
        """Analyze how message count varies each day."""
        daily_counts = Counter(datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d') for message in self.messages)
        return daily_counts
    
    def question_messages_count(self):
        """Number of messages containing questions."""
        return sum('?' in message.text_data for message in self.messages if message.text_data)

    def analyze(self):
        return {
            "Total Messages": self.total_messages(),
            "Messages by Sender": self.messages_by_sender(),
            "Average Messages per Day": self.average_messages_per_day(),
            "Day with Most Messages": self.day_with_most_messages(),
            "Most Common Words": self.most_common_words(),
            "Total Words Sent": self.total_words_sent(),
            "Average Word Count per Message": self.average_word_count_per_message(),
            "Messages per Hour": self.messages_per_hour(),
            "Longest Message": self.longest_message(),
            "Number of Emojis": self.number_of_emojis(),
            "Most Used Emoji": self.most_used_emojis(),
            "Photo Messages Count": self.photo_messages_count(),
            "Sticker Messages Count": self.sticker_messages_count(),
            "Video Messages Count": self.video_messages_count(),
            "Audio Messages Count": self.audio_messages_count(),
            "Location Messages Count": self.audio_messages_count(),
            "Messages on Special Dates": self.messages_on_special_dates(),
            "Good Morning/Night Messages": self.good_morning_night_messages(),
            "Days Without Messages": self.days_without_messages(),
            "Average Response Time": self.average_response_time(),
            "Count Love Messages": self.count_love_messages(),
            "Happy/Sad Words Count": self.happy_sad_words_count(),
            "Monthly Message Frequency Variation": self.monthly_frequency_variation(),
            "Daily Message Frequency Variation": self.daily_frequency_variation(),
            "Question Messages Count": self.question_messages_count()
        }
        