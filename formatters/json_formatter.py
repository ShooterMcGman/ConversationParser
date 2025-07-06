"""
JSON formatter for generating RAG-optimized JSON output files.
"""

import json
from typing import Dict, Any
from datetime import datetime


class JSONFormatter:
    """Formatter for creating structured JSON files optimized for RAG consumption."""
    
    def __init__(self):
        """Initialize the JSON formatter."""
        pass
    
    def write_json_file(self, week_data: Dict[str, Any], output_path: str) -> None:
        """
        Write week data to a JSON file optimized for RAG consumption.
        
        Args:
            week_data (Dict[str, Any]): Week data containing messages and metadata
            output_path (str): Path where the JSON file should be written
        """
        # Structure the data for optimal RAG consumption
        json_structure = {
            'metadata': {
                'format_version': '1.0',
                'generated_at': datetime.now().isoformat(),
                'week_info': week_data['week_info'],
                'global_week_number': week_data['global_week_number'],
                'conversation_metadata': week_data['conversation_metadata'],
                'summary': week_data['summary']
            },
            'messages': self._format_messages_for_json(week_data['messages']),
            'analytics': self._generate_analytics(week_data['messages']),
            'rag_optimization': {
                'chunking_strategy': 'weekly',
                'indexable_fields': [
                    'message_id', 'sender', 'type', 'sent_timestamp', 
                    'content', 'attachments', 'reactions'
                ],
                'searchable_content': self._extract_searchable_content(week_data['messages']),
                'temporal_context': {
                    'week_start': week_data['week_info']['week_start'],
                    'week_end': week_data['week_info']['week_end'],
                    'day_of_year': week_data['week_info'].get('day_of_year'),
                    'week_of_year': week_data['week_info'].get('week_of_year')
                }
            }
        }
        
        # Write JSON file with proper formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=2, ensure_ascii=False, sort_keys=False)
    
    def _format_messages_for_json(self, messages):
        """Format messages for JSON with enhanced metadata."""
        formatted_messages = []
        
        for i, message in enumerate(messages):
            formatted_message = {
                'message_id': message.get('message_id'),
                'sequence_in_week': i + 1,
                'conversation_id': message.get('conversation_id'),
                'sender': message.get('sender'),
                'type': message.get('type'),
                'timestamps': {
                    'sent': message.get('sent_timestamp'),
                    'received': message.get('received_timestamp')
                },
                'content': {
                    'text': message.get('content', ''),
                    'word_count': len(message.get('content', '').split()) if message.get('content') else 0,
                    'character_count': len(message.get('content', '')) if message.get('content') else 0
                },
                'metadata': {
                    'is_edited': message.get('is_edited', False),
                    'version_history': message.get('version_history', []),
                    'status': message.get('status', 'active')
                },
                'interactions': {
                    'quoted_message': message.get('quoted_message'),
                    'reactions': message.get('reactions', []),
                    'attachments': message.get('attachments', [])
                }
            }
            
            # Add temporal analysis
            if message.get('sent_timestamp'):
                formatted_message['temporal_analysis'] = self._analyze_message_timing(message)
            
            formatted_messages.append(formatted_message)
        
        return formatted_messages
    
    def _analyze_message_timing(self, message):
        """Analyze timing characteristics of a message."""
        try:
            timestamp = datetime.fromisoformat(message['sent_timestamp'].replace('Z', '+00:00'))
            
            return {
                'hour_of_day': timestamp.hour,
                'day_of_week': timestamp.weekday(),  # 0=Monday, 6=Sunday
                'is_weekend': timestamp.weekday() >= 5,
                'time_period': self._get_time_period(timestamp.hour),
                'date_only': timestamp.date().isoformat()
            }
        except (ValueError, TypeError):
            return None
    
    def _get_time_period(self, hour):
        """Get time period classification for an hour."""
        if 5 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 21:
            return 'evening'
        else:
            return 'night'
    
    def _generate_analytics(self, messages):
        """Generate analytics data for the message set."""
        analytics = {
            'message_stats': {
                'total_count': len(messages),
                'by_sender': {},
                'by_type': {},
                'by_hour': {},
                'by_day': {}
            },
            'content_stats': {
                'total_characters': 0,
                'total_words': 0,
                'average_message_length': 0,
                'longest_message': 0,
                'shortest_message': float('inf')
            },
            'interaction_stats': {
                'messages_with_attachments': 0,
                'messages_with_reactions': 0,
                'messages_with_quotes': 0,
                'total_attachments': 0
            }
        }
        
        total_length = 0
        valid_messages = 0
        
        for message in messages:
            # Sender stats
            sender = message.get('sender', 'Unknown')
            analytics['message_stats']['by_sender'][sender] = \
                analytics['message_stats']['by_sender'].get(sender, 0) + 1
            
            # Type stats
            msg_type = message.get('type', 'unknown')
            analytics['message_stats']['by_type'][msg_type] = \
                analytics['message_stats']['by_type'].get(msg_type, 0) + 1
            
            # Content stats
            content = message.get('content', '')
            if content:
                char_count = len(content)
                word_count = len(content.split())
                
                analytics['content_stats']['total_characters'] += char_count
                analytics['content_stats']['total_words'] += word_count
                analytics['content_stats']['longest_message'] = max(
                    analytics['content_stats']['longest_message'], char_count
                )
                analytics['content_stats']['shortest_message'] = min(
                    analytics['content_stats']['shortest_message'], char_count
                )
                
                total_length += char_count
                valid_messages += 1
            
            # Interaction stats
            if message.get('attachments'):
                analytics['interaction_stats']['messages_with_attachments'] += 1
                analytics['interaction_stats']['total_attachments'] += len(message['attachments'])
            
            if message.get('reactions'):
                analytics['interaction_stats']['messages_with_reactions'] += 1
            
            if message.get('quoted_message'):
                analytics['interaction_stats']['messages_with_quotes'] += 1
            
            # Temporal stats
            if message.get('sent_timestamp'):
                try:
                    timestamp = datetime.fromisoformat(message['sent_timestamp'].replace('Z', '+00:00'))
                    hour = timestamp.hour
                    day = timestamp.date().isoformat()
                    
                    analytics['message_stats']['by_hour'][hour] = \
                        analytics['message_stats']['by_hour'].get(hour, 0) + 1
                    analytics['message_stats']['by_day'][day] = \
                        analytics['message_stats']['by_day'].get(day, 0) + 1
                        
                except (ValueError, TypeError):
                    continue
        
        # Calculate averages
        if valid_messages > 0:
            analytics['content_stats']['average_message_length'] = total_length / valid_messages
        
        if analytics['content_stats']['shortest_message'] == float('inf'):
            analytics['content_stats']['shortest_message'] = 0
        
        return analytics
    
    def _extract_searchable_content(self, messages):
        """Extract searchable content for RAG indexing."""
        searchable_content = {
            'all_text': '',
            'content_by_sender': {},
            'keywords': [],
            'topics': []
        }
        
        all_text_parts = []
        
        for message in messages:
            content = message.get('content', '')
            sender = message.get('sender', 'Unknown')
            
            if content:
                all_text_parts.append(content)
                
                # Group by sender
                if sender not in searchable_content['content_by_sender']:
                    searchable_content['content_by_sender'][sender] = []
                searchable_content['content_by_sender'][sender].append(content)
        
        searchable_content['all_text'] = '\n'.join(all_text_parts)
        
        # Extract basic keywords (simple approach - can be enhanced)
        words = searchable_content['all_text'].lower().split()
        word_freq = {}
        for word in words:
            # Simple word filtering
            if len(word) > 3 and word.isalpha():
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        searchable_content['keywords'] = sorted(word_freq.items(), 
                                              key=lambda x: x[1], reverse=True)[:20]
        
        return searchable_content
