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
        # Create minimal week info from first message
        messages = week_data['messages']
        if not messages:
            return
            
        first_msg = messages[0]
        last_msg = messages[-1]
        
        # Enhanced structure for RAG optimization
        json_structure = {
            'metadata': {
                'format_version': '2.0',
                'generated_at': datetime.now().isoformat(),
                'global_week_number': week_data['global_week_number'],
                'week_start': first_msg.get('sent_timestamp', '')[:10],
                'week_end': last_msg.get('sent_timestamp', '')[:10],
                'total_messages': len(messages),
                'conversation_title': week_data['conversation_metadata'].get('conversation_title', ''),
                'rag_optimization': {
                    'content_types': self._analyze_content_types(messages),
                    'semantic_tags': self._generate_semantic_tags(messages),
                    'temporal_patterns': self._analyze_temporal_patterns(messages)
                }
            },
            'messages': self._format_messages_for_json_optimized(messages),
            'analytics': self._generate_analytics_optimized(messages),
            'content_index': self._create_content_index(messages),
            'conversation_flow': self._analyze_conversation_flow(messages)
        }
        
        # Write JSON file with compact formatting for large files
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=1, ensure_ascii=False, separators=(',', ':'))
    
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
    
    def _format_messages_for_json_optimized(self, messages):
        """Format messages for JSON with reduced memory usage."""
        formatted_messages = []
        
        for i, message in enumerate(messages):
            # Only include essential fields for large datasets
            formatted_message = {
                'id': message.get('message_id'),
                'seq': i + 1,
                'sender': message.get('sender'),
                'type': message.get('type'),
                'timestamp': message.get('sent_timestamp'),
                'content': message.get('content', ''),
                'attachments': len(message.get('attachments', [])),
                'has_quote': bool(message.get('quoted_message'))
            }
            
            formatted_messages.append(formatted_message)
        
        return formatted_messages
    
    def _generate_analytics_optimized(self, messages):
        """Generate simplified analytics for large datasets."""
        analytics = {
            'total_messages': len(messages),
            'by_sender': {},
            'by_type': {},
            'timespan': {
                'start': messages[0].get('sent_timestamp', '') if messages else '',
                'end': messages[-1].get('sent_timestamp', '') if messages else ''
            }
        }
        
        for message in messages:
            # Count by sender
            sender = message.get('sender', 'Unknown')
            analytics['by_sender'][sender] = analytics['by_sender'].get(sender, 0) + 1
            
            # Count by type
            msg_type = message.get('type', 'unknown')
            analytics['by_type'][msg_type] = analytics['by_type'].get(msg_type, 0) + 1
        
        return analytics
    
    def _analyze_content_types(self, messages):
        """Analyze types of content for RAG optimization."""
        content_types = {
            'text_only': 0,
            'with_attachments': 0,
            'with_quotes': 0,
            'with_reactions': 0,
            'edited_messages': 0
        }
        
        for message in messages:
            if message.get('attachments'):
                content_types['with_attachments'] += 1
            elif message.get('quoted_message'):
                content_types['with_quotes'] += 1
            elif message.get('reactions'):
                content_types['with_reactions'] += 1
            elif message.get('is_edited'):
                content_types['edited_messages'] += 1
            else:
                content_types['text_only'] += 1
        
        return content_types
    
    def _generate_semantic_tags(self, messages):
        """Generate semantic tags for content classification."""
        tags = []
        content_text = ' '.join([msg.get('content', '') for msg in messages]).lower()
        
        # Simple keyword-based tagging (can be enhanced with NLP)
        tag_keywords = {
            'planning': ['plan', 'schedule', 'meeting', 'calendar', 'appointment'],
            'emotional': ['love', 'miss', 'happy', 'sad', 'excited', 'worried'],
            'work': ['work', 'job', 'office', 'boss', 'project', 'deadline'],
            'travel': ['trip', 'flight', 'hotel', 'vacation', 'travel'],
            'food': ['dinner', 'lunch', 'restaurant', 'cooking', 'eat'],
            'family': ['mom', 'dad', 'sister', 'brother', 'family'],
            'health': ['doctor', 'hospital', 'medicine', 'sick', 'health']
        }
        
        for tag, keywords in tag_keywords.items():
            if any(keyword in content_text for keyword in keywords):
                tags.append(tag)
        
        return tags
    
    def _analyze_temporal_patterns(self, messages):
        """Analyze temporal communication patterns."""
        patterns = {
            'peak_hours': [],
            'most_active_day': '',
            'conversation_gaps': []
        }
        
        hourly_counts = {}
        daily_counts = {}
        
        for message in messages:
            timestamp_str = message.get('sent_timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hour = timestamp.hour
                    day = timestamp.strftime('%A')
                    
                    hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
                    daily_counts[day] = daily_counts.get(day, 0) + 1
                except (ValueError, TypeError):
                    continue
        
        # Find peak hours (top 3)
        if hourly_counts:
            patterns['peak_hours'] = sorted(hourly_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Find most active day
        if daily_counts:
            patterns['most_active_day'] = max(daily_counts.items(), key=lambda x: x[1])[0]
        
        return patterns
    
    def _create_content_index(self, messages):
        """Create a content index for efficient RAG retrieval."""
        index = {
            'by_sender': {},
            'by_content_length': {'short': [], 'medium': [], 'long': []},
            'with_keywords': {},
            'conversation_starters': []
        }
        
        for i, message in enumerate(messages):
            sender = message.get('sender', 'Unknown')
            content = message.get('content', '')
            
            # Index by sender
            if sender not in index['by_sender']:
                index['by_sender'][sender] = []
            index['by_sender'][sender].append(i)
            
            # Index by content length
            if content:
                length = len(content)
                if length < 50:
                    index['by_content_length']['short'].append(i)
                elif length < 200:
                    index['by_content_length']['medium'].append(i)
                else:
                    index['by_content_length']['long'].append(i)
                
                # Simple keyword indexing
                words = content.lower().split()
                for word in words:
                    if len(word) > 4 and word.isalpha():
                        if word not in index['with_keywords']:
                            index['with_keywords'][word] = []
                        index['with_keywords'][word].append(i)
        
        return index
    
    def _analyze_conversation_flow(self, messages):
        """Analyze conversation flow patterns."""
        flow = {
            'message_intervals': [],
            'response_patterns': {},
            'conversation_threads': []
        }
        
        prev_timestamp = None
        prev_sender = None
        
        for message in messages:
            current_sender = message.get('sender')
            timestamp_str = message.get('sent_timestamp')
            
            if timestamp_str and prev_timestamp:
                try:
                    current_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    interval = (current_time - prev_timestamp).total_seconds() / 60  # minutes
                    flow['message_intervals'].append(interval)
                except (ValueError, TypeError):
                    pass
            
            # Track response patterns
            if prev_sender and current_sender != prev_sender:
                pattern = f"{prev_sender} -> {current_sender}"
                flow['response_patterns'][pattern] = flow['response_patterns'].get(pattern, 0) + 1
            
            if timestamp_str:
                try:
                    prev_timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except (ValueError, TypeError):
                    pass
            prev_sender = current_sender
        
        return flow
    
    def write_daily_json_file(self, daily_data: Dict[str, Any], output_path: str) -> None:
        """
        Write daily data to a JSON file optimized for RAG consumption.
        
        Args:
            daily_data (Dict[str, Any]): Daily data containing messages and metadata
            output_path (str): Path where the daily JSON file should be written
        """
        messages = daily_data['messages']
        if not messages:
            return
            
        # Enhanced daily structure for RAG optimization
        json_structure = {
            'metadata': {
                'format_version': '2.0',
                'generated_at': datetime.now().isoformat(),
                'day_date': daily_data['day_date'],
                'day_name': daily_data['day_name'],
                'global_week_number': daily_data['global_week_number'],
                'total_messages': len(messages),
                'conversation_title': daily_data['conversation_metadata'].get('conversation_title', ''),
                'rag_optimization': {
                    'content_types': self._analyze_content_types(messages),
                    'semantic_tags': self._generate_semantic_tags(messages),
                    'temporal_patterns': self._analyze_daily_temporal_patterns(messages)
                }
            },
            'messages': self._format_messages_for_json_optimized(messages),
            'analytics': self._generate_analytics_optimized(messages),
            'content_index': self._create_content_index(messages),
            'daily_summary': self._generate_daily_summary(messages)
        }
        
        # Write JSON file with compact formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_structure, f, indent=1, ensure_ascii=False, separators=(',', ':'))
    
    def _analyze_daily_temporal_patterns(self, messages):
        """Analyze temporal patterns within a single day."""
        patterns = {
            'hourly_distribution': {},
            'conversation_peaks': [],
            'gaps_between_messages': []
        }
        
        prev_timestamp = None
        
        for message in messages:
            timestamp_str = message.get('sent_timestamp')
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    hour = timestamp.hour
                    
                    patterns['hourly_distribution'][hour] = patterns['hourly_distribution'].get(hour, 0) + 1
                    
                    if prev_timestamp:
                        gap_minutes = (timestamp - prev_timestamp).total_seconds() / 60
                        patterns['gaps_between_messages'].append(gap_minutes)
                    
                    prev_timestamp = timestamp
                except (ValueError, TypeError):
                    continue
        
        # Find conversation peaks (hours with most activity)
        if patterns['hourly_distribution']:
            sorted_hours = sorted(patterns['hourly_distribution'].items(), key=lambda x: x[1], reverse=True)
            patterns['conversation_peaks'] = sorted_hours[:3]
        
        return patterns
    
    def _generate_daily_summary(self, messages):
        """Generate a summary of daily conversation."""
        summary = {
            'message_count': len(messages),
            'participants': list(set(msg.get('sender', 'Unknown') for msg in messages)),
            'first_message_time': messages[0].get('sent_timestamp', '')[:16] if messages else '',
            'last_message_time': messages[-1].get('sent_timestamp', '')[:16] if messages else '',
            'content_highlights': []
        }
        
        # Simple content highlighting (longest messages)
        content_messages = [msg for msg in messages if msg.get('content')]
        if content_messages:
            content_messages.sort(key=lambda x: len(x.get('content', '')), reverse=True)
            summary['content_highlights'] = [
                {
                    'sender': msg.get('sender'),
                    'preview': msg.get('content', '')[:100] + '...' if len(msg.get('content', '')) > 100 else msg.get('content', ''),
                    'length': len(msg.get('content', ''))
                }
                for msg in content_messages[:3]
            ]
        
        return summary
