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
        content = self._generate_markdown_content(week_data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
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
