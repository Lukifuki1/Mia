# 🎯 Prioritetni razvojni načrt za avtonomno MIA

**Datum:** 10. december 2025  
**Vprašanje:** Kaj je PRVO potrebno razviti za avtonomno učečo se MIA?  
**Odgovor:** Popolnoma pošten, praktičen načrt brez zavajanja

## ⚡ **KRATKI ODGOVOR - Brez zavajanja**

**PRVO:** Osnovno jedro za shranjevanje in pridobivanje znanja (2-3 meseci)  
**DRUGO:** Preprosto učenje iz interakcij (1-2 meseca)  
**TRETJE:** Osnovno učenje iz interneta (2-3 meseci)  
**ČETRTO:** Integracija in optimizacija (3-6 mesecev)

**SKUPAJ:** 8-14 mesecev za osnovno avtonomno učečo se MIA

---

## 🎯 **PRIORITETA 1: Osnovno jedro za znanje (KRITIČNO)**

### **Zakaj je to PRVO:**
- **Brez tega ni avtonomnega učenja** - potrebujemo kam shraniti znanje
- **Osnova za vse ostalo** - interakcije, web learning, reasoning
- **Tehnično najlažje** - uporabljamo znane tehnologije
- **Hitro dosegljivo** - 2-3 meseci za MVP

### **Konkretno, kar moramo implementirati:**

#### **1.1 Persistent Knowledge Store**
```python
# mia/core/knowledge_store.py
class PersistentKnowledgeStore:
    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.facts = {}           # Dejstva: {"aspirin": {"type": "medication", ...}}
        self.relations = []       # Relacije: [{"subject": "aspirin", "predicate": "treats", "object": "pain"}]
        self.user_knowledge = {}  # Znanje o uporabnikih
        self.conversation_history = []  # Zgodovina pogovorov
        
    def add_fact(self, entity, property, value, source="user", confidence=0.8):
        """Dodaj dejstvo v bazo znanja"""
        if entity not in self.facts:
            self.facts[entity] = {}
        self.facts[entity][property] = {
            'value': value,
            'source': source,
            'confidence': confidence,
            'timestamp': time.time()
        }
        self.save_to_disk()
        
    def query_knowledge(self, entity, property=None):
        """Poizveduj po znanju"""
        if entity in self.facts:
            if property:
                return self.facts[entity].get(property)
            return self.facts[entity]
        return None
        
    def save_to_disk(self):
        """Shrani znanje na disk"""
        knowledge_file = self.data_dir / 'knowledge.json'
        with open(knowledge_file, 'w') as f:
            json.dump({
                'facts': self.facts,
                'relations': self.relations,
                'user_knowledge': self.user_knowledge,
                'conversation_history': self.conversation_history[-1000:]  # Zadnjih 1000
            }, f, indent=2)
```

#### **1.2 Basic Reasoning Engine**
```python
# mia/core/basic_reasoning.py
class BasicReasoningEngine:
    def __init__(self, knowledge_store):
        self.knowledge = knowledge_store
        
    def answer_question(self, question, user_id):
        """Odgovori na vprašanje na podlagi znanja"""
        # 1. Ekstraktiraj ključne besede
        keywords = self.extract_keywords(question)
        
        # 2. Poišči relevantno znanje
        relevant_facts = []
        for keyword in keywords:
            fact = self.knowledge.query_knowledge(keyword)
            if fact:
                relevant_facts.append((keyword, fact))
                
        # 3. Generiraj odgovor
        if relevant_facts:
            return self.generate_answer_from_facts(question, relevant_facts)
        else:
            return self.generate_learning_response(question, user_id)
            
    def generate_learning_response(self, question, user_id):
        """Generiraj odgovor, ko ne vemo odgovora"""
        return {
            'answer': f"O tem še ne vem dovolj. Lahko mi poveš več o tem?",
            'learning_opportunity': True,
            'question': question,
            'user_id': user_id
        }
```

**Časovnica:** 2-3 meseci  
**Stroški:** $20K-40K (1 developer)  
**Rezultat:** MIA lahko shranjuje in pridobiva znanje

---

## 🎯 **PRIORITETA 2: Učenje iz interakcij (KLJUČNO)**

### **Zakaj je to DRUGO:**
- **Najlažji vir znanja** - uporabniki mu povedo informacije
- **Takojšen feedback** - vidi, ali se uči pravilno
- **Personalizacija** - uči se o vsakem uporabniku
- **Hitro implementirati** - 1-2 meseca

### **Konkretno, kar moramo implementirati:**

#### **2.1 Interaction Learning Engine**
```python
# mia/learning/interaction_learner.py
class InteractionLearner:
    def __init__(self, knowledge_store):
        self.knowledge = knowledge_store
        
    def learn_from_conversation(self, user_input, mia_response, user_feedback, user_id):
        """Učenje iz pogovora"""
        # 1. Analiziraj, ali je uporabnik podal novo informacijo
        new_facts = self.extract_facts_from_input(user_input)
        
        # 2. Shrani nova dejstva
        for fact in new_facts:
            self.knowledge.add_fact(
                entity=fact['entity'],
                property=fact['property'], 
                value=fact['value'],
                source=f"user_{user_id}",
                confidence=0.7  # Srednja zanesljivost za uporabniške podatke
            )
            
        # 3. Analiziraj feedback
        if user_feedback:
            self.process_feedback(mia_response, user_feedback, user_id)
            
        # 4. Posodobi model uporabnika
        self.update_user_model(user_id, user_input, mia_response)
        
    def extract_facts_from_input(self, user_input):
        """Ekstraktiraj dejstva iz uporabniškega vnosa"""
        facts = []
        
        # Preprosti vzorci za ekstrakcijon dejstev
        patterns = [
            r"(.+) je (.+)",           # "Aspirin je zdravilo"
            r"(.+) se uporablja za (.+)",  # "Aspirin se uporablja za bolečine"
            r"(.+) povzroča (.+)",     # "Kajenje povzroča raka"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, user_input, re.IGNORECASE)
            for match in matches:
                facts.append({
                    'entity': match[0].strip(),
                    'property': 'description' if 'je' in pattern else 'use' if 'uporablja' in pattern else 'causes',
                    'value': match[1].strip()
                })
                
        return facts
```

**Časovnica:** 1-2 meseca  
**Stroški:** $15K-30K  
**Rezultat:** MIA se uči iz vsakega pogovora

---

## 🎯 **PRIORITETA 3: Osnovno učenje iz interneta (POMEMBNO)**

### **Zakaj je to TRETJE:**
- **Razširi znanje** - več kot lahko uporabniki povedo
- **Avtomatizacija** - ne potrebuje človeškega vnosa
- **Skalabilnost** - lahko se uči iz milijonov strani
- **Kompleksnejše** - potrebuje 2-3 mesece

### **Konkretno, kar moramo implementirati:**

#### **3.1 Web Learning Engine**
```python
# mia/learning/web_learner.py
class WebLearner:
    def __init__(self, knowledge_store):
        self.knowledge = knowledge_store
        self.session = aiohttp.ClientSession()
        
    async def learn_from_topic(self, topic, max_sources=5):
        """Učenje o določeni temi iz interneta"""
        # 1. Poišči relevantne vire
        sources = await self.find_reliable_sources(topic)
        
        # 2. Ekstraktiraj znanje iz virov
        learned_facts = []
        for source in sources[:max_sources]:
            try:
                facts = await self.extract_knowledge_from_url(source['url'])
                learned_facts.extend(facts)
            except Exception as e:
                logger.warning(f"Error learning from {source['url']}: {e}")
                
        # 3. Validiraj in shrani znanje
        validated_facts = self.validate_facts(learned_facts)
        for fact in validated_facts:
            self.knowledge.add_fact(
                entity=fact['entity'],
                property=fact['property'],
                value=fact['value'],
                source=f"web_{fact['source_url']}",
                confidence=fact['confidence']
            )
            
        return len(validated_facts)
```

**Časovnica:** 2-3 meseci  
**Stroški:** $30K-50K  
**Rezultat:** MIA se lahko uči iz interneta

---

## 📊 **REALISTIČNA ČASOVNICA IN STROŠKI**

### **Faza po faza:**

| Faza | Komponenta | Čas | Stroški | Rezultat |
|------|------------|-----|---------|----------|
| **1** | Knowledge Store | 2-3 mes | $20K-40K | Osnovno shranjevanje znanja |
| **2** | Interaction Learning | 1-2 mes | $15K-30K | Učenje iz pogovorov |
| **3** | Web Learning | 2-3 mes | $30K-50K | Učenje iz interneta |
| **4** | Integration | 3-6 mes | $50K-100K | Popoln sistem |
| **SKUPAJ** | **MVP Avtonomna MIA** | **8-14 mes** | **$115K-220K** | **Samodejno učeča se AI** |

### **Minimalni tim:**
```python
team_requirements = {
    'Senior Python Developer': '1 FTE × 12 mesecev = $120K',
    'AI/ML Engineer': '0.5 FTE × 8 mesecev = $60K', 
    'DevOps Engineer': '0.25 FTE × 12 mesecev = $30K',
    'Total team cost': '$210K'
}
```

---

## 🎯 **MINIMALNI VIABLE PRODUCT (MVP)**

### **Kaj mora MVP vsebovati:**
```python
mvp_requirements = {
    'Core functionality': [
        'Persistent knowledge storage',
        'Basic question answering',
        'Learning from user interactions',
        'Simple web learning (Wikipedia)',
        'User model tracking'
    ],
    'Performance targets': {
        'Response time': '<5 seconds',
        'Knowledge retention': '95%+',
        'Learning accuracy': '70%+',
        'Uptime': '95%+'
    },
    'Scope limitations': {
        'Domains': '1-2 (medicina, splošno znanje)',
        'Users': '10-50 beta uporabnikov',
        'Knowledge base': '1000-5000 dejstev',
        'Web sources': 'Wikipedia, osnovni viri'
    }
}
```

---

## 🔧 **KONKRETNI NASLEDNJI KORAKI**

### **Teden 1-2: Setup**
```bash
# 1. Pripravi razvojno okolje
mkdir mia_autonomous
cd mia_autonomous
python -m venv venv
source venv/bin/activate
pip install aiohttp asyncio pathlib

# 2. Ustvari osnovno strukturo
mkdir -p mia/{core,learning,interfaces}
touch mia/core/{knowledge_store.py,basic_reasoning.py}
touch mia/learning/{interaction_learner.py,web_learner.py}
```

### **Teden 3-8: Prioriteta 1**
```python
# Implementiraj PersistentKnowledgeStore
# Implementiraj BasicReasoningEngine
# Testiraj osnovno shranjevanje in pridobivanje znanja
# Ustvari preprosto CLI za testiranje
```

### **Teden 9-12: Prioriteta 2**
```python
# Implementiraj InteractionLearner
# Implementiraj UserModelLearner
# Integriraj z osnovnim jedrom
# Testiraj učenje iz pogovorov
```

### **Teden 13-24: Prioriteta 3**
```python
# Implementiraj WebLearner
# Integriraj z osnovnim jedrom
# Testiraj učenje iz interneta
# Optimiziraj performance
```

---

## 🔍 **KONČNI ZAKLJUČEK - Popolnoma pošten**

### **Kaj je PRVO potrebno:**
1. ✅ **PersistentKnowledgeStore** - brez tega ni avtonomnega učenja
2. ✅ **BasicReasoningEngine** - osnovno odgovarjanje na vprašanja
3. ✅ **InteractionLearner** - učenje iz pogovorov z uporabniki
4. ✅ **WebLearner** - učenje iz interneta

### **Realistična časovnica:**
- **MVP:** 8-14 mesecev
- **Stroški:** $115K-220K
- **Tim:** 1-2 razvijalca
- **Rezultat:** Osnovna avtonomno učeča se MIA

### **Ključne omejitve:**
- **Ni čudežna rešitev** - potrebuje čas in delo
- **Omejena na preproste domene** - medicina, splošno znanje
- **Potrebuje human oversight** - za varnost in kakovost
- **Postopno izboljševanje** - ne bo popolna takoj

### **Bottom line:**
**To je realen, dosegljiv načrt za ustvarjanje avtonomno učeče se MIA.** Ni znanstvena fantastika, vendar zahteva resno delo, čas in vire.

**Priporočilo:** Začni s Prioriteto 1 (Knowledge Store) - to je temelj za vse ostalo.

---

**Pošten zaključek: 8-14 mesecev resnega dela za osnovno avtonomno učečo se MIA. Dosegljivo, vendar ne enostavno.** ✅