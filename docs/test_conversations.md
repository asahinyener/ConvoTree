# ConvoTree Test Conversation Scenarios

## Test Conversation 1: Memory & Knowledge Building Test

**Scenario:** "Personal Assistant Knowledge Building"
**Duration:** 10-15 interactions
**Focus:** Knowledge retention, fact building, memory persistence

### Conversation Flow:

1. **User:** "Hi, I'm Sarah. I'm a software engineer working at TechCorp in San Francisco."
   - *Expected:* System should extract: name=Sarah, job=software engineer, company=TechCorp, location=San Francisco

2. **User:** "I'm working on a Python web scraping project for analyzing e-commerce data."
   - *Expected:* System should link: Sarah -> works_on -> Python project, project_type=web scraping, domain=e-commerce

3. **User:** "My favorite programming languages are Python and JavaScript. I prefer React for frontend work."
   - *Expected:* System should extract preferences: languages=[Python, JavaScript], frontend_preference=React

4. **User:** "I have a meeting with my manager John tomorrow at 2 PM to discuss the project timeline."
   - *Expected:* System should extract: manager=John, meeting_time=tomorrow 2PM, topic=project timeline

5. **User:** "What do you know about me so far?"
   - *Expected:* System should recall: name, job, company, location, project details, preferences, upcoming meeting

6. **User:** "I'm also learning machine learning in my spare time. I'm particularly interested in NLP and computer vision."
   - *Expected:* System should add: learning_interests=[machine learning, NLP, computer vision]

7. **User:** "My project deadline is next Friday. I'm a bit stressed about finishing the data pipeline in time."
   - *Expected:* System should extract: deadline=next Friday, stress_factor=data pipeline completion

8. **User:** "Can you remind me what I told you about my meeting tomorrow?"
   - *Expected:* System should recall: meeting with John at 2PM about project timeline

9. **User:** "I live in the Mission District and usually take the BART to work."
   - *Expected:* System should extract: neighborhood=Mission District, transportation=BART

10. **User:** "What would you suggest for my Python web scraping project based on what I've told you?"
    - *Expected:* System should synthesize information about: Python project, e-commerce data, deadline pressure, expertise level

### Success Criteria:
- **Knowledge Growth:** 15+ new facts extracted
- **Memory Retention:** Accurate recall of personal details
- **Context Integration:** Responses reference previous information
- **Fact Relationships:** Knowledge graph shows connections between entities

---

## Test Conversation 2: Complex Reasoning & Context Test

**Scenario:** "Technical Problem Solving"
**Duration:** 12-18 interactions  
**Focus:** Reasoning, context switching, knowledge synthesis

### Conversation Flow:

1. **User:** "I'm debugging a performance issue in my React application. The initial page load takes 8 seconds."
   - *Expected:* System should understand: problem=performance issue, technology=React, symptom=slow page load (8s)

2. **User:** "The app has a large dashboard with 20+ data visualization components. Each component makes its own API call."
   - *Expected:* System should identify potential cause: multiple API calls, large component count

3. **User:** "My bundle size is currently 2.5MB. I'm using Chart.js, Moment.js, and several other heavy libraries."
   - *Expected:* System should note: bundle_size=2.5MB, libraries=[Chart.js, Moment.js], potential optimization target

4. **User:** "What do you think is causing the performance issue?"
   - *Expected:* System should synthesize: bundle size + multiple API calls + heavy libraries = performance problem

5. **User:** "I tried code splitting but it didn't help much. The dashboard still loads slowly."
   - *Expected:* System should note: attempted_solution=code splitting, result=minimal improvement

6. **User:** "Let me switch topics - do you know any good techniques for React optimization?"
   - *Expected:* System should provide React optimization advice while maintaining context of the specific problem

7. **User:** "Going back to my specific issue - I just realized all 20 API calls happen simultaneously on page load."
   - *Expected:* System should connect this new info to the established problem context

8. **User:** "The API calls are fetching different types of data: user analytics, sales metrics, inventory levels, and performance KPIs."
   - *Expected:* System should categorize data types and understand the scale of simultaneous requests

9. **User:** "Each API call takes about 200-500ms. Since they're all parallel, what's causing the 8-second delay?"
   - *Expected:* System should reason: parallel calls (200-500ms) shouldn't cause 8s delay, must be another factor

10. **User:** "Wait, I think the issue might be that the components are re-rendering constantly. How can I check this?"
    - *Expected:* System should suggest React DevTools, profiling tools, identify re-rendering as likely culprit

11. **User:** "You were right about re-rendering. I see thousands of unnecessary renders. What's the best way to fix this?"
    - *Expected:* System should suggest: React.memo, useMemo, useCallback, component optimization

12. **User:** "After implementing React.memo and optimizing renders, my load time dropped to 1.2 seconds! What should I tackle next?"
    - *Expected:* System should acknowledge success and suggest: bundle optimization, lazy loading, caching strategies

### Success Criteria:
- **Problem Analysis:** Correctly identifies multiple contributing factors
- **Context Switching:** Maintains context when topic changes and returns
- **Reasoning Chain:** Shows logical problem-solving progression  
- **Solution Synthesis:** Combines technical knowledge with specific problem details
- **Adaptive Learning:** Updates understanding as new information is provided

---

## Expected Recording Metrics

### Performance Targets:
- **Response Time:** < 3 seconds average
- **Knowledge Extraction:** 2-3 new facts per interaction
- **Context Usage:** 3-5 relevant facts referenced per response
- **Consistency:** No contradictory information

### Quality Indicators:
- **Fact Accuracy:** All extracted information should be correct
- **Relationship Mapping:** Clear connections between entities
- **Context Continuity:** References to previous conversation elements
- **Progressive Understanding:** Knowledge builds appropriately over time

## Testing Protocol:

1. **Start CLI:** `python chat_cli.py --conversation-id test_session_1`
2. **Begin Recording:** `/record memory_test`
3. **Execute Conversation 1:** Follow scenario exactly
4. **Stop Recording:** `/stop`
5. **Switch Conversation:** `/new test_session_2`
6. **Begin Recording:** `/record reasoning_test`
7. **Execute Conversation 2:** Follow scenario exactly  
8. **Stop Recording:** `/stop`
9. **Analysis:** `/replay` for both recordings

## Post-Test Analysis Points:

- Knowledge graph visualization comparison
- Response time patterns
- Context utilization efficiency
- Error handling and recovery
- Memory consistency across sessions