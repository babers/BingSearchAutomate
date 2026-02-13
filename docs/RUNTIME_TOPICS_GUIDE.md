# Quick Reference: Runtime Topic Generation

**Version**: 1.0  
**Date**: February 7, 2026

---

## 🚀 Quick Start

### Default Behavior (No Changes Needed!)

The app now uses **RuntimeTopicGenerator by default**:

```yaml
# config.yaml
search_settings:
  topic_generator: 'runtime'  # ← Generates topics dynamically
```

Run normally:

```bash
python main.py
```

Topics generated automatically at runtime!

---

## 📋 Quick Reference Table

| Feature | Before | After |

        $dashes = $Matches[1]
        "| $dashes |"
    -------- 
        $dashes = $Matches[1]
        "| $dashes |"
    
| **Topics** | 50-60 per day | Infinite! |
| **Update topics** | Edit Python code | Edit config.yaml? No! (generated dynamically) |
| **Variety** | Limited | Unlimited combinations |
| **New trending topic** | Requires deployment | Just happens automatically |
| **Search query examples** | "Role of Zoology in Conservation" | "Mysterious elephant migration tutorial 2024" |

---

## ⚙️ Configuration Options

### Use Runtime Generator (Recommended)

```yaml
search_settings:
  topic_generator: 'runtime'
```

**Result**: `get_next_topic()` generates new topics each time

### Use Legacy Daily Topics

```yaml
search_settings:
  topic_generator: 'daily'
```

**Result**: Uses Monday-Sunday topic lists (original behavior)

---

## 🎯 Example Generated Topics

The RuntimeTopicGenerator creates natural-sounding search queries by combining:

### Template #1: Adjective + Noun

- "Rare dolphin migration patterns"
- "Mysterious AI algorithms"
- "Endangered species tourism"

### Template #2: Noun + Activity

- "Tiger hunting techniques"
- "Whale communication behaviors"
- "Blockchain security challenges"

### Template #3: Adjective + Noun + Activity + Verb

- "Endangered tiger migration behavior explained"
- "Modern AI ethics tutorial"
- "Rare bird hunting guide 2024"

### Template #4: Noun + Verb + Context

- "Quantum computing best practices 2024"
- "Machine learning tutorial for beginners"
- "Cryptocurrency vs traditional banking"

---

## 🔧 How It Works

```python
# This now just works:
generator = RuntimeTopicGenerator()

# Get topic #1
topic = generator.get_next_topic()
# → "Fascinating wolf communication tutorial"

# Get topic #2
topic = generator.get_next_topic()
# → "Rare machine learning guide for beginners"

# Get topic #3
topic = generator.get_next_topic()
# → "Ancient Egyptian architecture explained"

# Check stats
stats = generator.get_statistics()
# → {'generated_count': 3, 'unique_topics': 3, ...}

# Reset for new session
generator.reset()
```

---

## 🔌 Plugin Architecture

The **TopicProvider interface** means you can easily swap implementations:

```python
# In config.yaml, just change:
topic_generator: 'runtime'   # or
topic_generator: 'daily'     # or later...
topic_generator: 'trending'  # custom implementation
```

Example custom provider:

```python
class TrendingTopicsProvider(TopicProvider):
    def get_next_topic(self):
        return self.fetch_from_twitter_trends()
    
    def reset(self):
        self.cache.clear()
    
    def get_statistics(self):
        return {'trending_from': 'twitter'}
```

Then just update config and it works!

---

## 📊 Word Pools (Customizable)

The RuntimeTopicGenerator uses these word categories:

### Noun Categories

- **animals**: dog, cat, elephant, dolphin, whale, chimpanzee, parrot, eagle, etc.
- **tech**: AI, machine learning, blockchain, quantum computing, cloud storage, etc.
- **science**: DNA, photosynthesis, cell division, mutation, evolution, etc.
- **history**: ancient Rome, medieval period, Renaissance, Industrial Revolution, etc.
- **geography**: Amazon rainforest, Mount Everest, Sahara desert, Arctic, etc.
- **business**: startup, marketing, financial planning, investment, etc.

### Modifiers

- **Adjectives**: endangered, ancient, rare, modern, advanced, basic, mysterious, etc.
- **Activities**: communication, migration, hunting, mating, behavior, reproduction, etc.
- **Verbs**: explained, tutorial, guide, analysis, best practices, tips and tricks, etc.
- **Contexts**: 2024, in 2025, future predictions, history of, recent developments, etc.

Want to add more topics? Simply extend the word pools in `utils/runtime_topic_generator.py`:

```python
# Add to NOUNS['animals']
'flamingo', 'porcupine', 'fennec fox', 'meerkat'

# Add to ADJECTIVES
'beautiful', 'terrifying', 'friendly', 'intelligent'

# Add to ACTIVITIES
'hibernation', 'metamorphosis', 'symbiosis', 'adaptation'
```

---

## 🧪 Testing

### Test App Initialization

```bash
python -c "from main import Application; from config import Config; \
           cfg = Config.from_yaml(); app = Application(cfg); print('✓ OK')"
```

### Test RuntimeTopicGenerator Directly

```python
from utils.runtime_topic_generator import RuntimeTopicGenerator

gen = RuntimeTopicGenerator()
for i in range(5):
    print(f"{i+1}. {gen.get_next_topic()}")

print(gen.get_statistics())
```

**Output**:

```text
1. Fascinating whale hunting patterns guide
2. Endangered tiger migration behavior explained
3. Modern AI ethics vs traditional approaches
4. Ancient Roman architecture tutorial 2024
5. Rare bird communication skills for beginners
{'generated_count': 5, 'unique_topics': 5, 'generator_type': 'RuntimeTopicGenerator'}
```

---

## 🔍 Troubleshooting

### Issue: Getting same topic twice

**Solution**: RuntimeTopicGenerator has deduplication - it tracks generated topics per session. If you see duplicates:

1. Check that cache_duplicates=True in config
2. Increase max_generation_attempts if hitting limit
3. Or reset generator between sessions

### Issue: Topics don't seem natural

**Solution**:

1. Review the word pools in `runtime_topic_generator.py`
2. Adjust templates (lines 120-130) to generate better combinations
3. Consider LLM-based generator for production use

### Issue: Want specific topics

**Solution**:

1. Switch to 'daily' mode in config.yaml
2. Or create custom TopicProvider class
3. Or pre-filter RuntimeTopicGenerator output

---

## 📝 Log Output Example

```text
INFO: Initializing application components...
INFO: Using RuntimeTopicGenerator for dynamic topic generation
INFO: RuntimeTopicGenerator initialized (cache_duplicates=True)
INFO: BrowserController initialized
INFO: Application components initialized successfully.
DEBUG: Generated topic #1: "Mysterious whale communication behavior explained"
DEBUG: Generated topic #2: "Ancient Roman architecture tutorial 2024"
INFO: Starting search for topic: Mysterious whale communication behavior explained
INFO: Search completed, points: 35
DEBUG: Generated topic #3: "Rare quantum computing best practices"
```

---

## 🎓 Key Concepts

### TopicProvider (Interface)

All topic providers implement this interface:

- `get_next_topic()` → str: Get the next topic
- `reset()`: Clear state for new session
- `get_statistics()` → dict: Get generation stats

### RuntimeTopicGenerator

Generates topics dynamically using word templates and random selection.

- ✅ Infinite variety
- ✅ No external API calls
- ✅ Configurable deduplication
- ✅ Fast (< 1ms per topic)

### DailyTopics (Legacy)

Pre-compiled topic lists organized by day of week.

- ✅ Backward compatible
- ⚠️ Static (50-60 topics per day)
- ⚠️ Requires code changes to update

---

## 🚀 Next Steps

1. **Test with real searches**: Run app with RuntimeTopicGenerator and see if Bing accepts all generated topics
2. **Customize word pools**: Add domain-specific terms for your use case
3. **Monitor results**: Check if any generated topics don't get good rewards
4. **Consider enhancements**: LLM-based generator for even better topics

---

## 📚 See Also

- Full architectural review: `ARCHITECTURAL_REVIEW.md`
- Implementation details: `IMPLEMENTATION_SUMMARY.md`
- Code source: `utils/runtime_topic_generator.py`
- Configuration: `config.yaml` (search_settings.topic_generator)
