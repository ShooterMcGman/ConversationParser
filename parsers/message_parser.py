"""
Message parser module for extracting structured data from conversation text files.
"""

import re
from datetime import datetime
from typing import List, Dict, Any, Optional


class MessageParser:
    """Parser for extracting messages and metadata from conversation text files."""
    
    def __init__(self):
        """Initialize the message parser with regex patterns."""
        # Regex patterns for parsing different elements
        self.conversation_pattern = r'^Conversation:\s*(.+)$'
        self.from_pattern = r'^From:\s*(.+)$'
        self.type_pattern = r'^Type:\s*(.+)$'
        self.sent_pattern = r'^Sent:\s*(.+)$'
        self.received_pattern = r'^Received:\s*(.+)$'
        self.attachment_pattern = r'^Attachment:\s*(.+)$'
        self.reaction_pattern = r'^Reaction:\s*(.+)\s+by\s+(.+)$'
        self.quote_pattern = r'^>\s*(.+)$'
        
    def parse_messages(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse all messages from the conversation content.
        
        Args:
            content (str): Raw conversation text content
            
        Returns:
            List[Dict[str, Any]]: List of parsed message objects
        """
        lines = content.split('\n')
        messages = []
        current_message = None
        message_counter = 1
        
        # Pre-compile regex patterns for better performance
        from_re = re.compile(self.from_pattern)
        type_re = re.compile(self.type_pattern)
        sent_re = re.compile(self.sent_pattern)
        received_re = re.compile(self.received_pattern)
        attachment_re = re.compile(self.attachment_pattern)
        quote_re = re.compile(self.quote_pattern)
        conversation_re = re.compile(self.conversation_pattern)
        metadata_re = re.compile(r'^(From|Type|Sent|Received|Attachment):')
        
        print(f"Processing {len(lines)} lines...")
        
        i = 0
        progress_counter = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Progress reporting for large files
            progress_counter += 1
            if progress_counter % 10000 == 0:
                print(f"Processed {progress_counter}/{len(lines)} lines ({progress_counter/len(lines)*100:.1f}%)")
            
            # Skip empty lines
            if not line:
                i += 1
                continue
            
            # Check for conversation header (skip it)
            if conversation_re.match(line):
                i += 1
                continue
            
            # Check for new message start (From: line)
            from_match = from_re.match(line)
            if from_match:
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)
                
                # Start new message
                current_message = {
                    'message_id': f"msg_{message_counter:04d}",
                    'sender': from_match.group(1).strip(),
                    'type': 'unknown',
                    'sent_timestamp': None,
                    'received_timestamp': None,
                    'content': '',
                    'is_edited': False,
                    'version_history': [],
                    'quoted_message': None,
                    'reactions': [],
                    'attachments': [],
                    'status': 'active'
                }
                message_counter += 1
                i += 1
                continue
            
            # Parse message metadata if we have a current message
            if current_message:
                # Parse type
                type_match = type_re.match(line)
                if type_match:
                    current_message['type'] = type_match.group(1).strip()
                    i += 1
                    continue
                
                # Parse sent timestamp
                sent_match = sent_re.match(line)
                if sent_match:
                    timestamp_str = sent_match.group(1).strip()
                    current_message['sent_timestamp'] = self._parse_timestamp(timestamp_str)
                    i += 1
                    continue
                
                # Parse received timestamp
                received_match = received_re.match(line)
                if received_match:
                    timestamp_str = received_match.group(1).strip()
                    current_message['received_timestamp'] = self._parse_timestamp(timestamp_str)
                    i += 1
                    continue
                
                # Parse attachment
                attachment_match = attachment_re.match(line)
                if attachment_match:
                    attachment_info = self._parse_attachment(attachment_match.group(1).strip())
                    if attachment_info:
                        current_message['attachments'].append(attachment_info)
                    i += 1
                    continue
                
                # Parse quoted message
                quote_match = quote_re.match(line)
                if quote_match:
                    if not current_message['quoted_message']:
                        current_message['quoted_message'] = {'content': ''}
                    current_message['quoted_message']['content'] += quote_match.group(1) + '\n'
                    i += 1
                    continue
                
                # Check if this starts a new message (another From: line)
                if from_re.match(line):
                    continue  # Let the outer loop handle this
                
                # Otherwise, this is message content
                if line and not metadata_re.match(line):
                    if current_message['content']:
                        current_message['content'] += '\n'
                    current_message['content'] += line
            
            i += 1
        
        # Add the last message
        if current_message:
            messages.append(current_message)
        
        print(f"Extracted {len(messages)} messages. Post-processing...")
        
        # Post-process messages
        return self._post_process_messages(messages)
    
    def _parse_timestamp(self, timestamp_str: str) -> Optional[str]:
        """
        Parse timestamp string into ISO 8601 format.
        
        Args:
            timestamp_str (str): Raw timestamp string
            
        Returns:
            Optional[str]: ISO 8601 formatted timestamp or None
        """
        try:
            # Handle various timestamp formats
            timestamp_formats = [
                '%a, %d %b %Y %H:%M:%S %z',  # Sun, 13 Apr 2025 20:48:54 -0400
                '%d %b %Y %H:%M:%S %z',      # 13 Apr 2025 20:48:54 -0400
                '%Y-%m-%d %H:%M:%S %z',      # 2025-04-13 20:48:54 -0400
                '%Y-%m-%d %H:%M:%S',         # 2025-04-13 20:48:54
            ]
            
            for fmt in timestamp_formats:
                try:
                    dt = datetime.strptime(timestamp_str, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            # If no format matches, return the original string
            return timestamp_str
            
        except Exception as e:
            print(f"Warning: Could not parse timestamp '{timestamp_str}': {e}")
            return None
    
    def _parse_attachment(self, attachment_str: str) -> Optional[Dict[str, Any]]:
        """
        Parse attachment information.
        
        Args:
            attachment_str (str): Raw attachment string
            
        Returns:
            Optional[Dict[str, Any]]: Parsed attachment info or None
        """
        try:
            # Parse attachment format: "filename (mime/type, size bytes)"
            # Example: "no filename (image/png, 68224 bytes)"
            pattern = r'^(.+?)\s*\(([^,]+),\s*(\d+)\s*bytes\)$'
            match = re.match(pattern, attachment_str)
            
            if match:
                filename = match.group(1).strip()
                mime_type = match.group(2).strip()
                size_bytes = int(match.group(3))
                
                return {
                    'file_name': filename if filename != 'no filename' else None,
                    'mime_type': mime_type,
                    'size_bytes': size_bytes
                }
            
            # If parsing fails, return raw info
            return {
                'file_name': None,
                'mime_type': 'unknown',
                'size_bytes': 0,
                'raw_info': attachment_str
            }
            
        except Exception as e:
            print(f"Warning: Could not parse attachment '{attachment_str}': {e}")
            return None
    
    def _post_process_messages(self, messages: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Post-process messages to clean up content and detect patterns.
        
        Args:
            messages (List[Dict[str, Any]]): Raw parsed messages
            
        Returns:
            List[Dict[str, Any]]: Processed messages
        """
        for message in messages:
            # Clean up content
            if message['content']:
                message['content'] = message['content'].strip()
            
            # Clean up quoted message content
            if message['quoted_message'] and message['quoted_message'].get('content'):
                message['quoted_message']['content'] = message['quoted_message']['content'].strip()
            
            # Detect if message was deleted
            if 'deleted' in message.get('type', '').lower():
                message['status'] = 'deleted'
            
            # Set conversation_id for all messages
            if messages:
                # Extract from first message or use a default
                conversation_id = self._extract_conversation_id(messages)
                message['conversation_id'] = conversation_id
        
        return messages
    
    def _extract_conversation_id(self, messages: List[Dict[str, Any]]) -> str:
        """Extract conversation ID from messages."""
        # Look for patterns in sender names to identify the conversation
        senders = set()
        for message in messages:
            sender = message.get('sender', '')
            if sender and sender != 'You':
                senders.add(sender)
        
        if senders:
            # Use the first non-"You" sender as conversation ID
            return sorted(senders)[0]
        
        return 'Unknown Conversation'
    
    def extract_conversation_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extract metadata about the entire conversation.
        
        Args:
            content (str): Raw conversation content
            
        Returns:
            Dict[str, Any]: Conversation metadata
        """
        lines = content.split('\n')
        
        # Extract conversation title from first line
        conversation_title = None
        for line in lines:
            match = re.match(self.conversation_pattern, line)
            if match:
                conversation_title = match.group(1).strip()
                break
        
        # Extract participants
        participants = set()
        for line in lines:
            match = re.match(self.from_pattern, line)
            if match:
                sender = match.group(1).strip()
                participants.add(sender)
        
        return {
            'conversation_title': conversation_title,
            'participants': list(participants),
            'extraction_timestamp': datetime.now().isoformat(),
            'total_lines': len(lines)
        }
