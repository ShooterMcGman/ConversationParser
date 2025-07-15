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
        """Group messages by week for output organization with optimized performance."""
        self.weekly_groups = defaultdict(list)
        
        processed_count = 0
        invalid_count = 0
        
        # Pre-compile date format for faster parsing
        from dateutil.parser import isoparse
        
        for message in self.messages:
            processed_count += 1
            if processed_count % 5000 == 0:
                print(f"Grouped {processed_count}/{len(self.messages)} messages ({processed_count/len(self.messages)*100:.1f}%)")
            
            timestamp_str = message.get('sent_timestamp')
            if timestamp_str:
                try:
                    # Use faster date parsing
                    timestamp = isoparse(timestamp_str)
                    
                    # Create simpler week key for better performance
                    week_start = timestamp.date() - timedelta(days=(timestamp.weekday() + 1) % 7)
                    week_key = week_start.strftime('%Y-%m-%d')
                    
                    self.weekly_groups[week_key].append(message)
                    
                except (ValueError, TypeError):
                    invalid_count += 1
                    if invalid_count % 100 == 0:
                        print(f"Warning: {invalid_count} messages with invalid timestamps")
                    continue
        
        print(f"Grouped {processed_count} messages into {len(self.weekly_groups)} weekly groups")
    
    def _group_messages_by_day(self, messages):
        """Group messages by day within a week."""
        daily_groups = defaultdict(list)
        
        from dateutil.parser import isoparse
        
        for message in messages:
            timestamp_str = message.get('sent_timestamp')
            if timestamp_str:
                try:
                    timestamp = isoparse(timestamp_str)
                    day_key = timestamp.strftime('%Y-%m-%d')
                    daily_groups[day_key].append(message)
                except (ValueError, TypeError):
                    continue
        
        return dict(daily_groups)
    
    def generate_output(self):
        """
        Generate JSON and Markdown files organized by week with daily breakdowns and create a zip archive.
        
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
            
            # Create simplified folder name from week key and first message
            first_timestamp = messages[0].get('sent_timestamp', '')
            start_date = first_timestamp[:10] if first_timestamp else 'unknown'
            
            # Create structured output directories
            json_weeks_dir = os.path.join(output_dir, "JSON", "weeks")
            json_days_dir = os.path.join(output_dir, "JSON", "days")
            md_weeks_dir = os.path.join(output_dir, "MD", "weeks")
            md_days_dir = os.path.join(output_dir, "MD", "days")
            
            for dir_path in [json_weeks_dir, json_days_dir, md_weeks_dir, md_days_dir]:
                os.makedirs(dir_path, exist_ok=True)
            
            # Group messages by day for daily files
            daily_groups = self._group_messages_by_day(messages)
            
            # Generate week file names
            week_filename = f"week_{global_week_number}"
            json_path = os.path.join(json_weeks_dir, f"{week_filename}.json")
            md_path = os.path.join(md_weeks_dir, f"{week_filename}.md")
            
            # Prepare simplified week data for large datasets
            week_data = {
                'global_week_number': global_week_number,
                'conversation_metadata': self.conversation_metadata,
                'messages': messages
            }
            
            # Generate JSON file
            self.json_formatter.write_json_file(week_data, json_path)
            
            # Generate Markdown file
            self.markdown_formatter.write_markdown_file(week_data, md_path)
            
            # Generate daily files (both JSON and MD)
            for day_key, day_messages in daily_groups.items():
                if day_messages:
                    day_name = datetime.strptime(day_key, '%Y-%m-%d').strftime('%A')
                    daily_filename = f"day_{day_key}_{day_name}"
                    
                    daily_json_path = os.path.join(json_days_dir, f"{daily_filename}.json")
                    daily_md_path = os.path.join(md_days_dir, f"{daily_filename}.md")
                    
                    daily_data = {
                        'global_week_number': global_week_number,
                        'day_date': day_key,
                        'day_name': day_name,
                        'conversation_metadata': self.conversation_metadata,
                        'messages': day_messages
                    }
                    
                    # Generate daily JSON file
                    self.json_formatter.write_daily_json_file(daily_data, daily_json_path)
                    
                    # Generate daily MD file
                    self.markdown_formatter.write_daily_markdown_file(daily_data, daily_md_path)
            
            print(f"Generated week {global_week_number}: {len(messages)} messages with {len(daily_groups)} daily files")
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
