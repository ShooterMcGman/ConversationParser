"""
Markdown formatter for generating RAG-optimized Markdown output files.
"""

from typing import Dict, Any
from datetime import datetime
import re


class MarkdownFormatter:
    """Formatter for creating structured Markdown files optimized for RAG consumption."""
    
    def __init__(self):
        """Initialize the Markdown formatter."""
        pass
    
    def write_markdown_file(self, week_data: Dict[str, Any], output_path: str) -> None:
        """
        Write week data to a Markdown file optimized for RAG consumption.
        
        Args:
            week_data (Dict[str, Any]): Week data containing messages and metadata
            output_path (str): Path where the Markdown file should be written
        """
        # Generate content in chunks for large datasets
        messages = week_data['messages']
        if not messages:
            return
            
        # Write header and metadata first
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self._generate_header_optimized(week_data))
            f.write('\n\n')
            f.write(self._generate_metadata_optimized(week_data))
            f.write('\n\n')
            
            # Write messages in chunks to reduce memory usage
            f.write('## 💬 Conversation Messages\n\n')
            
            chunk_size = 100  # Process 100 messages at a time
            for i in range(0, len(messages), chunk_size):
                chunk = messages[i:i + chunk_size]
                for j, message in enumerate(chunk, i + 1):
                    f.write(self._format_message_optimized(message, j))
                    f.write('\n\n---\n\n')
    
    def write_daily_markdown_file(self, daily_data: Dict[str, Any], output_path: str) -> None:
        """
        Write daily data to a Markdown file optimized for RAG consumption.
        
        Args:
            daily_data (Dict[str, Any]): Daily data containing messages and metadata
            output_path (str): Path where the daily Markdown file should be written
        """
        messages = daily_data['messages']
        if not messages:
            return
            
        with open(output_path, 'w', encoding='utf-8') as f:
            # Daily header
            f.write(f"# Daily Conversation: {daily_data['day_date']} ({daily_data['day_name']})\n\n")
            
            # Metadata section
            f.write("## 📅 Daily Metadata\n\n")
            f.write("| Field | Value |\n")
            f.write("|-------|-------|\n")
            f.write(f"| **Date** | {daily_data['day_date']} |\n")
            f.write(f"| **Day** | {daily_data['day_name']} |\n")
            f.write(f"| **Week** | {daily_data['global_week_number']} |\n")
            f.write(f"| **Messages** | {len(messages)} |\n")
            
            # Quick stats
            senders = set(msg.get('sender', 'Unknown') for msg in messages)
            f.write(f"| **Participants** | {', '.join(senders)} |\n")
            f.write(f"| **Time Range** | {messages[0].get('sent_timestamp', '')[:16]} - {messages[-1].get('sent_timestamp', '')[:16]} |\n\n")
            
            # Daily summary
            f.write("## 📝 Daily Summary\n\n")
            f.write(f"This day contains **{len(messages)} messages** exchanged ")
            if len(senders) > 1:
                f.write(f"between {' and '.join(senders)}. ")
            f.write(f"The conversation spans from morning to evening with various topics covered.\n\n")
            
            # Content tags for RAG
            content_text = ' '.join([msg.get('content', '') for msg in messages]).lower()
            tags = self._generate_daily_tags(content_text)
            if tags:
                f.write("**Content Tags:** ")
                f.write(", ".join([f"`{tag}`" for tag in tags]))
                f.write("\n\n")
            
            # Messages section
            f.write("## 💬 Messages\n\n")
            
            for i, message in enumerate(messages, 1):
                f.write(self._format_daily_message(message, i))
                f.write('\n\n')
    
    def _generate_daily_tags(self, content_text):
        """Generate content tags for daily files."""
        tags = []
        
        # Simple keyword-based tagging
        tag_keywords = {
            'morning': ['morning', 'breakfast', 'wake', 'coffee'],
            'work': ['work', 'office', 'meeting', 'job'],
            'evening': ['evening', 'dinner', 'night'],
            'planning': ['plan', 'schedule', 'later', 'tomorrow'],
            'emotional': ['love', 'miss', 'happy', 'excited'],
            'travel': ['drive', 'trip', 'go', 'come'],
            'food': ['eat', 'food', 'lunch', 'dinner']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def _format_daily_message(self, message, sequence_num):
        """Format a message for daily files with enhanced metadata."""
        timestamp = message.get('sent_timestamp', '')
        time_only = timestamp[11:16] if len(timestamp) >= 16 else 'Unknown'
        sender = message.get('sender', 'Unknown')
        content = message.get('content', '')
        
        formatted = f"**{sequence_num:03d}.** `{time_only}` **{sender}**\n\n"
        
        if content:
            # Format content with better readability
            formatted_content = self._format_message_content(content)
            formatted += f"{formatted_content}\n"
        
        # Add metadata if present
        metadata_parts = []
        if message.get('attachments'):
            metadata_parts.append(f"📎 {len(message['attachments'])} attachment(s)")
        if message.get('quoted_message'):
            metadata_parts.append("💬 Reply")
        if message.get('is_edited'):
            metadata_parts.append("✏️ Edited")
        
        if metadata_parts:
            formatted += f"\n*{' • '.join(metadata_parts)}*"
        
        return formatted
    
    def _generate_markdown_content(self, week_data: Dict[str, Any]) -> str:
        """Generate the complete Markdown content for a week."""
        sections = []
        
        # Header and metadata
        sections.append(self._generate_header(week_data))
        sections.append(self._generate_metadata_section(week_data))
        sections.append(self._generate_summary_section(week_data))
        
        # Main conversation content
        sections.append(self._generate_conversation_section(week_data['messages']))
        
        # Analytics and appendices
        sections.append(self._generate_analytics_section(week_data['messages']))
        sections.append(self._generate_participants_section(week_data))
        
        return '\n\n'.join(sections)
    
    def _generate_header(self, week_data: Dict[str, Any]) -> str:
        """Generate the main header for the document."""
        week_info = week_data['week_info']
        global_week = week_data['global_week_number']
        
        header = f"""# Week {global_week}: {week_info['month_name']} {week_info['year']} - Week {week_info['week_in_month']}

**Date Range:** {week_info['week_start']} to {week_info['week_end']}  
**Conversation:** {week_data['conversation_metadata'].get('conversation_title', 'Unknown')}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---"""
        
        return header
    
    def _generate_metadata_section(self, week_data: Dict[str, Any]) -> str:
        """Generate the metadata section."""
        metadata = week_data['conversation_metadata']
        week_info = week_data['week_info']
        
        section = """## 📊 Week Metadata

| Field | Value |
|-------|-------|"""
        
        section += f"\n| **Week Number** | {week_data['global_week_number']} |"
        section += f"\n| **Date Range** | {week_info['week_start']} to {week_info['week_end']} |"
        section += f"\n| **Total Messages** | {week_data['summary']['total_messages']} |"
        section += f"\n| **Participants** | {', '.join(week_data['summary']['participants'])} |"
        section += f"\n| **Message Types** | {', '.join(week_data['summary']['message_types'].keys())} |"
        
        if week_data['summary'].get('date_range'):
            section += f"\n| **First Message** | {week_data['summary']['date_range']['start_date']} |"
            section += f"\n| **Last Message** | {week_data['summary']['date_range']['end_date']} |"
        
        return section
    
    def _generate_summary_section(self, week_data: Dict[str, Any]) -> str:
        """Generate the weekly summary section."""
        summary = week_data['summary']
        
        section = """## 📋 Weekly Summary

### Message Type Breakdown
"""
        
        for msg_type, count in summary['message_types'].items():
            section += f"- **{msg_type.title()}**: {count} messages\n"
        
        section += f"\n### Key Statistics\n"
        section += f"- Total messages: {summary['total_messages']}\n"
        section += f"- Active participants: {len(summary['participants'])}\n"
        
        return section
    
    def _generate_conversation_section(self, messages) -> str:
        """Generate the main conversation section."""
        section = """## 💬 Conversation Messages

*Messages are presented in chronological order with full metadata for RAG optimization.*

"""
        
        for i, message in enumerate(messages, 1):
            section += self._format_message_markdown(message, i)
            section += "\n\n---\n\n"
        
        return section.rstrip("\n---\n")
    
    def _format_message_markdown(self, message, sequence_num) -> str:
        """Format a single message in Markdown."""
        msg_id = message.get('message_id', f'msg_{sequence_num:04d}')
        sender = message.get('sender', 'Unknown')
        msg_type = message.get('type', 'unknown')
        content = message.get('content', '')
        
        # Header
        msg_md = f"### Message {sequence_num}: {msg_id}\n\n"
        
        # Metadata table
        msg_md += "| Field | Value |\n|-------|-------|\n"
        msg_md += f"| **Sender** | {self._escape_markdown(sender)} |\n"
        msg_md += f"| **Type** | `{msg_type}` |\n"
        
        if message.get('sent_timestamp'):
            timestamp = self._format_timestamp_display(message['sent_timestamp'])
            msg_md += f"| **Sent** | {timestamp} |\n"
        
        if message.get('received_timestamp'):
            timestamp = self._format_timestamp_display(message['received_timestamp'])
            msg_md += f"| **Received** | {timestamp} |\n"
        
        msg_md += f"| **Status** | {message.get('status', 'active')} |\n"
        
        # Content
        if content:
            msg_md += f"\n**Content:**\n\n"
            # Format content with proper escaping and line breaks
            formatted_content = self._format_message_content(content)
            msg_md += formatted_content
        
        # Quoted message
        if message.get('quoted_message') and message['quoted_message'].get('content'):
            msg_md += f"\n\n**Quoted Message:**\n\n"
            quoted_content = self._format_quoted_content(message['quoted_message']['content'])
            msg_md += quoted_content
        
        # Attachments
        if message.get('attachments'):
            msg_md += f"\n\n**Attachments:**\n\n"
            for i, attachment in enumerate(message['attachments'], 1):
                msg_md += self._format_attachment(attachment, i)
        
        # Reactions
        if message.get('reactions'):
            msg_md += f"\n\n**Reactions:**\n\n"
            for reaction in message['reactions']:
                reactor = reaction.get('reactor', 'Unknown')
                reaction_type = reaction.get('reaction_type', '❓')
                msg_md += f"- {reaction_type} by {self._escape_markdown(reactor)}\n"
        
        # Version history
        if message.get('is_edited') and message.get('version_history'):
            msg_md += f"\n\n**Edit History:**\n\n"
            for version in message['version_history']:
                version_num = version.get('version_number', '?')
                version_timestamp = self._format_timestamp_display(version.get('version_timestamp', ''))
                msg_md += f"- **Version {version_num}** ({version_timestamp})\n"
        
        return msg_md
    
    def _format_message_content(self, content: str) -> str:
        """Format message content with proper Markdown formatting."""
        # Escape any existing markdown and preserve line breaks
        content = self._escape_markdown(content)
        
        # Convert line breaks to proper markdown
        lines = content.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                # Check if line looks like a list item
                if re.match(r'^\s*[•\-\*]\s', line):
                    formatted_lines.append(f"- {line[1:].strip()}")
                else:
                    formatted_lines.append(line)
            else:
                formatted_lines.append('')
        
        return '\n'.join(formatted_lines)
    
    def _format_quoted_content(self, content: str) -> str:
        """Format quoted message content."""
        lines = content.strip().split('\n')
        quoted_lines = [f"> {line}" for line in lines]
        return '\n'.join(quoted_lines)
    
    def _format_attachment(self, attachment: Dict[str, Any], index: int) -> str:
        """Format attachment information."""
        filename = attachment.get('file_name', 'No filename')
        mime_type = attachment.get('mime_type', 'unknown')
        size_bytes = attachment.get('size_bytes', 0)
        
        # Convert bytes to human readable format
        size_display = self._format_file_size(size_bytes)
        
        attachment_md = f"{index}. **{self._escape_markdown(filename)}**\n"
        attachment_md += f"   - Type: `{mime_type}`\n"
        attachment_md += f"   - Size: {size_display}\n"
        
        return attachment_md
    
    def _format_file_size(self, bytes_size: int) -> str:
        """Convert bytes to human readable format."""
        if bytes_size < 1024:
            return f"{bytes_size} bytes"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
    
    def _format_timestamp_display(self, timestamp_str: str) -> str:
        """Format timestamp for display."""
        try:
            if timestamp_str:
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                return dt.strftime('%Y-%m-%d %H:%M:%S %Z')
        except (ValueError, TypeError):
            pass
        return timestamp_str or 'Unknown'
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special Markdown characters."""
        if not text:
            return ''
        
        # Escape common markdown characters
        escape_chars = ['\\', '`', '*', '_', '{', '}', '[', ']', '(', ')', '#', '+', '-', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def _generate_analytics_section(self, messages) -> str:
        """Generate analytics section for the week."""
        section = """## 📈 Weekly Analytics

### Message Distribution by Sender
"""
        
        # Count messages by sender
        sender_counts = {}
        hour_counts = {}
        
        for message in messages:
            sender = message.get('sender', 'Unknown')
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
            
            # Count by hour
            if message.get('sent_timestamp'):
                try:
                    dt = datetime.fromisoformat(message['sent_timestamp'].replace('Z', '+00:00'))
                    hour = dt.hour
                    hour_counts[hour] = hour_counts.get(hour, 0) + 1
                except (ValueError, TypeError):
                    continue
        
        # Sender distribution
        for sender, count in sorted(sender_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(messages)) * 100
            section += f"- **{self._escape_markdown(sender)}**: {count} messages ({percentage:.1f}%)\n"
        
        # Time distribution
        if hour_counts:
            section += "\n### Message Distribution by Hour\n"
            for hour in sorted(hour_counts.keys()):
                count = hour_counts[hour]
                time_display = f"{hour:02d}:00"
                section += f"- **{time_display}**: {count} messages\n"
        
        return section
    
    def _generate_participants_section(self, week_data: Dict[str, Any]) -> str:
        """Generate participants section."""
        participants = week_data['summary']['participants']
        
        section = """## 👥 Participants

"""
        
        for i, participant in enumerate(participants, 1):
            section += f"{i}. **{self._escape_markdown(participant)}**\n"
        
        section += f"""
---

*This document was automatically generated from conversation data and optimized for RAG (Retrieval-Augmented Generation) consumption. All timestamps are preserved in ISO 8601 format for temporal analysis.*

**Document Metadata:**
- Format Version: 1.0
- Week Number: {week_data['global_week_number']}
- Total Messages: {week_data['summary']['total_messages']}
- Generation Time: {datetime.now().isoformat()}"""
        
        return section
    
    def _generate_header_optimized(self, week_data: Dict[str, Any]) -> str:
        """Generate optimized header for large datasets."""
        messages = week_data['messages']
        first_msg = messages[0] if messages else {}
        last_msg = messages[-1] if messages else {}
        
        start_date = first_msg.get('sent_timestamp', '')[:10]
        end_date = last_msg.get('sent_timestamp', '')[:10]
        
        header = f"""# Week {week_data['global_week_number']}: Conversation Messages

**Date Range:** {start_date} to {end_date}  
**Total Messages:** {len(messages)}  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---"""
        
        return header
    
    def _generate_metadata_optimized(self, week_data: Dict[str, Any]) -> str:
        """Generate simplified metadata for large datasets."""
        messages = week_data['messages']
        
        # Count participants and message types
        participants = set()
        msg_types = {}
        
        for msg in messages:
            participants.add(msg.get('sender', 'Unknown'))
            msg_type = msg.get('type', 'unknown')
            msg_types[msg_type] = msg_types.get(msg_type, 0) + 1
        
        section = f"""## 📊 Week Summary

- **Week Number:** {week_data['global_week_number']}
- **Messages:** {len(messages)}
- **Participants:** {len(participants)}
- **Message Types:** {', '.join(msg_types.keys())}"""
        
        return section
    
    def _format_message_optimized(self, message, sequence_num) -> str:
        """Format message with minimal processing for large datasets."""
        msg_id = message.get('message_id', f'msg_{sequence_num:04d}')
        sender = message.get('sender', 'Unknown')
        content = message.get('content', '')
        timestamp = message.get('sent_timestamp', '')
        
        # Simplified format for faster processing
        msg_md = f"### {sequence_num}. {msg_id}\n\n"
        msg_md += f"**{self._escape_markdown(sender)}** - {timestamp[:19]}\n\n"
        
        if content:
            # Limit content length for very large messages
            if len(content) > 1000:
                content = content[:1000] + "... [truncated]"
            msg_md += f"{self._escape_markdown(content)}\n"
        
        # Add attachment count if present
        attachments = message.get('attachments', [])
        if attachments:
            msg_md += f"\n*{len(attachments)} attachment(s)*\n"
        
        return msg_md
