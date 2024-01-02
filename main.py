import sys
from src.data_loader import DataLoader
from src.analysis import Analyzer

DB_PATH = "data/msgstore.db"  # Fixed path to the .db file

def main(conversation_id):
    # Load data from the .db file
    data_loader = DataLoader(DB_PATH)
    messages = data_loader.load_messages(conversation_id)  # Load messages from the specified conversation

    # Perform analysis
    analyzer = Analyzer(messages)
    
    # Get all statistics for the specific conversation
    stats = analyzer.analyze()

    # Display or save the analysis results
    print(f"Statistics for Conversation {conversation_id}:")
    for stat, value in stats.items():
        print(f"{stat}: {value}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python main.py conversation_id")
        sys.exit(1)

    conversation_id = int(sys.argv[1])  # Get the conversation ID from the command line
    main(conversation_id)
