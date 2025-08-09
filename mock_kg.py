"""
Mock implementation of KG functions for testing.
"""

class KnowledgePrioritizer:
    """Mock implementation of KnowledgePrioritizer."""
    
    def prioritize_kg(self, kg, current_topic=None, max_triples=None):
        """Prioritize knowledge graph triples based on relevance to current topic."""
        if not current_topic or not kg:
            return kg[:max_triples] if max_triples else kg
        
        # Simple prioritization: put triples containing words from the current topic first
        topic_words = current_topic.lower().split()
        
        # Score each triple based on how many topic words it contains
        scored_triples = []
        for triple in kg:
            score = 0
            triple_lower = triple.lower()
            for word in topic_words:
                if len(word) > 3 and word in triple_lower:  # Only consider words longer than 3 chars
                    score += 1
            scored_triples.append((score, triple))
        
        # Sort by score (descending)
        sorted_triples = [t for _, t in sorted(scored_triples, key=lambda x: x[0], reverse=True)]
        
        # Return top N triples if max_triples is specified
        if max_triples:
            return sorted_triples[:max_triples]
        return sorted_triples

def normalize_kg(kg):
    """Normalize a knowledge graph."""
    return kg

def compress_chat(messages):
    """Mock implementation of compress_chat."""
    # Create a simple KG based on the messages
    kg = []
    
    # Extract topics from user messages
    for i, msg in enumerate(messages):
        if msg["role"] == "user":
            content = msg["content"].lower()
            
            # Add Miles Davis related facts
            if "miles davis" in content:
                kg.append("Miles Davis|is a|legendary jazz musician")
                kg.append("Miles Davis|played|trumpet")
                kg.append("Miles Davis|released|Kind of Blue")
                kg.append("Miles Davis|was born in|1926")
                kg.append("Miles Davis|died in|1991")
            
            # Add instrument related facts
            if "instrument" in content:
                kg.append("Miles Davis|played|trumpet")
                kg.append("Miles Davis|also played|piano")
                kg.append("Trumpet|is a|brass instrument")
                kg.append("Miles Davis|was known for|his distinctive playing style")
            
            # Add album related facts
            if "album" in content:
                kg.append("Kind of Blue|is an album by|Miles Davis")
                kg.append("Kind of Blue|was released in|1959")
                kg.append("Bitches Brew|is an album by|Miles Davis")
                kg.append("Bitches Brew|was released in|1970")
                kg.append("Birth of the Cool|is an album by|Miles Davis")
                kg.append("Birth of the Cool|was released in|1957")
            
            # Add John Coltrane related facts
            if "coltrane" in content:
                kg.append("John Coltrane|is a|legendary jazz saxophonist")
                kg.append("John Coltrane|played with|Miles Davis")
                kg.append("John Coltrane|released|A Love Supreme")
                kg.append("John Coltrane|was born in|1926")
                kg.append("John Coltrane|died in|1967")
                kg.append("John Coltrane|was known for|sheets of sound technique")
            
            # Add influence related facts
            if "influence" in content:
                kg.append("Miles Davis|influenced|modern jazz")
                kg.append("Miles Davis|pioneered|cool jazz")
                kg.append("Miles Davis|pioneered|modal jazz")
                kg.append("Miles Davis|pioneered|jazz fusion")
                kg.append("Miles Davis|was one of|the most important figures in 20th-century music")
            
            # Add some facts based on message index to simulate KG growth
            if i > 0:
                kg.append(f"User|asked about|{content[:20]}...")
            if i > 1:
                kg.append(f"Conversation|is about|jazz musicians")
            if i > 2:
                kg.append(f"User|is interested in|jazz history")
    
    # Remove duplicates
    kg = list(set(kg))
    
    return {"kg": kg}

def resume_chat(bundle, user_input, current_topic=None):
    """Mock implementation of resume_chat."""
    # Generate a simple response based on the user input
    response = ""
    
    if "miles davis" in user_input.lower():
        response = "Miles Davis was one of the most influential jazz musicians of the 20th century. He was a trumpeter, bandleader, and composer who played a crucial role in the development of jazz."
    
    elif "instrument" in user_input.lower():
        response = "Miles Davis primarily played the trumpet. He was known for his distinctive playing style, characterized by his use of space, his lyrical phrasing, and his innovative approach to improvisation."
    
    elif "album" in user_input.lower():
        response = "Miles Davis released many influential albums throughout his career. His most famous album is 'Kind of Blue' (1959), which is often regarded as the greatest jazz album of all time. Other notable albums include 'Bitches Brew' (1970) and 'Birth of the Cool' (1957)."
    
    elif "coltrane" in user_input.lower():
        response = "John Coltrane was a legendary jazz saxophonist who collaborated with Miles Davis in the 1950s. He was known for his 'sheets of sound' technique and his spiritual approach to music. His album 'A Love Supreme' is considered one of the greatest jazz albums ever recorded."
    
    elif "influence" in user_input.lower():
        response = "Miles Davis had an enormous influence on jazz and popular music. He pioneered several jazz movements, including cool jazz, modal jazz, and jazz fusion. His innovative approach to music and his willingness to experiment with different styles and sounds made him one of the most important figures in 20th-century music."
    
    else:
        response = "I'm not sure what specific information you're looking for about Miles Davis or jazz. Could you please clarify your question?"
    
    return {"assistant_reply": response}