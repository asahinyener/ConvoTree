#!/usr/bin/env python3
"""
Interactive Demo Session
Runs a conversation with the enhanced chat system and saves responses
"""

import os
import json
from datetime import datetime
import dotenv

# Load environment variables
dotenv.load_dotenv()

from enhanced_chat import EnhancedChatSystem

def run_interactive_demo():
    """Run interactive demo session"""
    
    # Start interactive session
    chat = EnhancedChatSystem('interactive_demo', 'interactive_demo.db')

    # Conversation turns
    turns = [
        'Hi! I am Alex, a data scientist working at a startup called DataFlow in Austin.',
        'I am working on a machine learning project to predict customer churn for our SaaS platform.',
        'We have about 50,000 customers and I am using Python with scikit-learn and pandas.',
        'My biggest challenge is dealing with imbalanced data - only 5% of customers actually churn.',
        'What do you know about me and my project so far?',
        'I am considering using SMOTE for handling the class imbalance. What do you think?',
        'Actually, I just realized I also need to present my findings to the CEO next Tuesday.',
        'The CEO is particularly interested in feature importance and business impact.',
        'Can you help me think about how to explain machine learning concepts to a non-technical executive?'
    ]

    session_data = {
        'session_id': 'interactive_demo',
        'timestamp': datetime.now().isoformat(),
        'conversation': []
    }

    print('Starting Interactive Demo Session...')
    print('=' * 60)

    for i, user_input in enumerate(turns, 1):
        print(f'\nTurn {i}:')
        print(f'User: {user_input}')
        
        try:
            result = chat.process_message(user_input)
            response = result['response']
            
            print(f'Assistant: {response}')
            
            # Store turn data
            turn_data = {
                'turn': i,
                'user_input': user_input,
                'assistant_response': response,
                'context_used': result.get('context_used', {}),
                'knowledge_extracted': result.get('knowledge_extracted', {})
            }
            
            session_data['conversation'].append(turn_data)
            
            entities = result.get('knowledge_extracted', {}).get('entities', [])
            relations = result.get('knowledge_extracted', {}).get('relations', [])
            print(f'[Knowledge extracted: {len(entities)} entities, {len(relations)} relations]')
            
        except Exception as e:
            print(f'Error: {e}')
            import traceback
            traceback.print_exc()
            break

    print('\n' + '=' * 60)
    print('Interactive session completed!')

    # Save to file
    with open('interactive_session_demo.json', 'w') as f:
        json.dump(session_data, f, indent=2)

    print('Session saved to interactive_session_demo.json')
    
    return session_data

if __name__ == "__main__":
    run_interactive_demo()