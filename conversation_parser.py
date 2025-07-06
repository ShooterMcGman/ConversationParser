"""
Main conversation parser module that coordinates the parsing and output generation process.
"""

import os
import zipfile
from datetime import datetime, timedelta
from collections import defaultdict
import json

from parsers.message_parser import MessageParser
from formatters.json_formatter import JSONFormatter
from formatters.markdown_formatter import MarkdownFormatter
from utils.date_utils import DateUtils
from utils.file_utils import FileUtils


class ConversationParser:
    """Main parser class that orchestrates the conversation parsing process."""
    
    def __init__(self):
        """Initialize the conversation parser."""
        self.message_parser = MessageParser()
        self.json_formatter = JSONFormatter()
        self.markdown_formatter = MarkdownFormatter()
        self.date_utils = DateUtils()
        self.file_utils = FileUtils()
        
        self.messages = []
        self.conversation_metadata = {}
        self.weekly_groups = {}
        
    def parse_file(self, file_path):
        """
        Parse a conversation file and extract all messages.
        
        Args:
            file_path (str): Path to the conversation text file
        """
        print(f"Reading file: {file_path}")
        
        # Check file size for memory management
        file_size = os.path.getsize(file_path)
        print(f"File size: {file_size / (1024*1024):.1f} MB")
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        print(f"File loaded into memory. Starting message parsing...")
        
        # Parse messages from the file content
        self.messages = self.message_parser.parse_messages(content)
        
        # Extract conversation metadata
        self.conversation_metadata = self.message_parser.extract_conversation_metadata(content)
        
        # Clear content from memory to save space
        del content
        
        print(f"Parsed {len(self.messages)} messages from conversation")
        
        # Group messages by week
        print("Organizing messages by week...")
        self._group_messages_by_week()
        
        print(f"Organized into {len(self.weekly_groups)} weekly groups")
    
    def _group_messages_by_week(self):
        """Group messages by week for output organization."""
        self.weekly_groups = defaultdict(list)
        
        processed_count = 0
        
        for message in self.messages:
            processed_count += 1
            if processed_count % 1000 == 0:
                print(f"Grouped {processed_count}/{len(self.messages)} messages ({processed_count/len(self.messages)*100:.1f}%)")
            
            if message.get('sent_timestamp'):
                try:
                    # Parse the timestamp
                    timestamp = datetime.fromisoformat(message['sent_timestamp'].replace('Z', '+00:00'))
                    
                    # Get the week info
                    week_info = self.date_utils.get_week_info(timestamp)
                    week_key = f"{week_info['year']}-{week_info['month']:02d}-W{week_info['week_in_month']}"
                    
                    self.weekly_groups[week_key].append(message)
                    
                except (ValueError, TypeError) as e:
                    print(f"Warning: Could not parse timestamp for message {message.get('message_id', 'unknown')}: {e}")
                    continue
    
    def generate_output(self):
        """
        Generate JSON and Markdown files organized by week and create a zip archive.
        
        Returns:
            str: Path to the generated zip file
        """
        output_dir = "parsed_conversations"
        zip_filename = f"parsed_conversations_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        # Clean up existing output directory
        if os.path.exists(output_dir):
            self.file_utils.remove_directory(output_dir)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Sort weekly groups chronologically
        sorted_weeks = sorted(self.weekly_groups.keys())
        
        global_week_number = 1
        
        total_weeks = len(sorted_weeks)
        print(f"Generating {total_weeks} weekly files...")
        
        for week_index, week_key in enumerate(sorted_weeks, 1):
            messages = self.weekly_groups[week_key]
            
            if not messages:
                continue
            
            print(f"Processing week {week_index}/{total_weeks} ({global_week_number}): {len(messages)} messages")
            
            # Get week information for folder naming
            first_message_timestamp = datetime.fromisoformat(
                messages[0]['sent_timestamp'].replace('Z', '+00:00')
            )
            week_info = self.date_utils.get_week_info(first_message_timestamp)
            
            # Create folder name
            folder_name = self.date_utils.get_week_folder_name(week_info, global_week_number)
            folder_path = os.path.join(output_dir, folder_name)
            os.makedirs(folder_path, exist_ok=True)
            
            # Generate file names
            base_filename = folder_name
            json_filename = f"{base_filename}.json"
            md_filename = f"{base_filename}.md"
            
            json_path = os.path.join(folder_path, json_filename)
            md_path = os.path.join(folder_path, md_filename)
            
            # Prepare week data
            week_data = {
                'week_info': week_info,
                'global_week_number': global_week_number,
                'conversation_metadata': self.conversation_metadata,
                'messages': messages,
                'summary': {
                    'total_messages': len(messages),
                    'message_types': self._get_message_type_counts(messages),
                    'date_range': self._get_date_range(messages),
                    'participants': list(set(msg.get('sender', 'Unknown') for msg in messages))
                }
            }
            
            # Generate JSON file
            self.json_formatter.write_json_file(week_data, json_path)
            
            # Generate Markdown file
            self.markdown_formatter.write_markdown_file(week_data, md_path)
            
            print(f"Generated week {global_week_number}: {folder_name}")
            global_week_number += 1
        
        # Create zip file
        zip_path = self._create_zip_archive(output_dir, zip_filename)
        
        return zip_path
    
    def _get_message_type_counts(self, messages):
        """Get counts of different message types."""
        type_counts = defaultdict(int)
        for message in messages:
            msg_type = message.get('type', 'unknown')
            type_counts[msg_type] += 1
        return dict(type_counts)
    
    def _get_date_range(self, messages):
        """Get the date range for a group of messages."""
        timestamps = []
        for message in messages:
            if message.get('sent_timestamp'):
                try:
                    ts = datetime.fromisoformat(message['sent_timestamp'].replace('Z', '+00:00'))
                    timestamps.append(ts)
                except (ValueError, TypeError):
                    continue
        
        if timestamps:
            timestamps.sort()
            return {
                'start_date': timestamps[0].isoformat(),
                'end_date': timestamps[-1].isoformat()
            }
        return None
    
    def _create_zip_archive(self, output_dir, zip_filename):
        """Create a zip archive of the parsed conversations."""
        zip_path = zip_filename
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, os.path.dirname(output_dir))
                    zipf.write(file_path, arcname)
        
        return zip_path
