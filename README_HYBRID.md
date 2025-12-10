# 🧠 MIA Hybrid System - Neural-Symbolic AI Integration

## 🎯 **PREGLED**

MIA Hybrid System je napredna implementacija hibridne umetne inteligence, ki združuje:
- **Neural Processing** (Semantic Layer)
- **Symbolic Reasoning** (Deterministic Reasoning Engine)
- **Knowledge Management** (Hybrid Knowledge Bank)
- **Autonomous Learning** (Pattern Recognition & Self-Improvement)
- **Unified Integration** z obstoječimi MIA komponentami

## ✨ **KLJUČNE FUNKCIONALNOSTI**

### 🏗️ **Hibridna Arhitektura**
- **6-slojni hibridni sistem** z neural-symbolic integration
- **Backward compatibility** z obstoječim MIA sistemom
- **Adaptive mode selection** - avtomatska izbira najboljšega načina
- **Fallback mechanisms** za stabilnost in zanesljivost

### 🧠 **Komponente Sistema**

#### 1. **Knowledge Bank Core**
- RDF/OWL ontologija z RDFLib
- SPARQL endpoint z optimizacijo
- Async operations za performance
- Backup sistem z timestamped backups
- Validation system z circular dependency detection

#### 2. **Semantic Layer**
- Sentence embeddings z SentenceTransformers
- Named Entity Recognition (spaCy + NLTK)
- Relation extraction z pattern matching
- Semantic similarity z cosine similarity
- Knowledge Bank integration

#### 3. **Deterministic Reasoning Engine**
- Rule-based sistem z različnimi tipi pravil
- Forward in backward chaining inference
- Z3 solver integration za constraint solving
- Explanation traces za razložljivost
- Consistency checking z contradiction detection

#### 4. **Hybrid Pipeline**
- Neural-symbolic integration orchestration
- Multi-stage processing (6 stopenj)
- Adaptive mode selection
- Result fusion z confidence aggregation
- Async operations za performance

#### 5. **Autonomous Learning**
- Incremental learning iz interakcij
- Pattern recognition z ML algoritmi (DBSCAN clustering)
- Knowledge extraction iz uporabniških interakcij
- Memory management in consolidation
- Quality assurance mechanisms

#### 6. **Hybrid Integration**
- Backward compatibility z AGI Core
- Seamless integration z Persistent Knowledge Store
- Unified API interface
- Fallback mechanisms
- Performance monitoring

## 🚀 **HITRI ZAGON**

### **Predpogoji**
```bash
# Python 3.8+
python --version

# Namesti odvisnosti
pip install -r requirements_hybrid.txt

# Opcijsko: spaCy model
python -m spacy download en_core_web_sm
```

### **Osnovni Zagon**
```bash
# Zaženi hibridni sistem
python mia_hybrid_launcher.py

# Odpri browser na: http://localhost:8000
```

### **Napredne Možnosti**
```bash
# Različni načini delovanja
python mia_hybrid_launcher.py --mode hybrid_enhanced
python mia_hybrid_launcher.py --mode adaptive
python mia_hybrid_launcher.py --mode classic

# Konfiguracija
python mia_hybrid_launcher.py --web-port 8080 --data-dir /path/to/data
python mia_hybrid_launcher.py --log-level DEBUG --no-browser

# Pomoč
python mia_hybrid_launcher.py --help
```

## 🔧 **NAČINI DELOVANJA**

### **1. Classic Mode**
- Samo obstoječi MIA sistem
- AGI Core + Persistent Knowledge Store
- Backward compatibility

### **2. Hybrid Mode**
- Samo hibridni sistem
- Vsi hibridni komponenti aktivni
- Napredne AI funkcionalnosti

### **3. Hybrid Enhanced Mode** ⭐ **PRIPOROČENO**
- Hibridni sistem z classic fallback
- Najboljše iz obeh svetov
- Maksimalna zanesljivost

### **4. Adaptive Mode**
- Avtomatska izbira načina
- Optimizacija glede na tip zahteve
- Inteligentno preklapljanje

## 📊 **ZMOGLJIVOSTI SISTEMA**

### **Capability Levels**
- **BASIC**: Osnovne funkcionalnosti
- **ENHANCED**: Hibridne funkcionalnosti
- **ADVANCED**: Napredne AI funkcionalnosti
- **EXPERT**: Polne hibridne zmogljivosti

### **Komponente Status**
```
✅ Knowledge Bank Core - RDF/OWL, SPARQL
✅ Semantic Layer - Embeddings, NER, Relations
✅ Reasoning Engine - Rules, Chaining, Z3
✅ Hybrid Pipeline - Neural-Symbolic Integration
✅ Autonomous Learning - Pattern Recognition
✅ Integration Layer - Unified API
```

## 🌐 **Web Interface**

### **Funkcionalnosti**
- **Chat Interface** - Interaktivni pogovor z MIA
- **Real-time Statistics** - Monitoring sistema
- **System Health** - Status komponent
- **Processing Modes** - Izbira načina delovanja

### **API Endpoints**
```
GET  /health          - Health check
GET  /api/stats       - System statistics
GET  /api/capabilities - System capabilities
POST /api/process     - Process request
```

## 📁 **Struktura Projekta**

```
Mia/
├── mia/
│   ├── core/
│   │   ├── agi_core.py
│   │   ├── persistent_knowledge_store.py
│   │   └── hybrid_integration.py
│   └── knowledge/
│       └── hybrid/
│           ├── knowledge_bank_core.py
│           ├── semantic_layer.py
│           ├── deterministic_reasoning.py
│           ├── hybrid_pipeline.py
│           └── autonomous_learning.py
├── mia_hybrid_launcher.py
├── requirements_hybrid.txt
└── README_HYBRID.md
```

## 🔬 **Testiranje**

### **Komponente Testi**
```bash
# Test posameznih komponent
python -m mia.knowledge.hybrid.knowledge_bank_core
python -m mia.knowledge.hybrid.semantic_layer
python -m mia.knowledge.hybrid.deterministic_reasoning
python -m mia.knowledge.hybrid.hybrid_pipeline
python -m mia.knowledge.hybrid.autonomous_learning
```

### **Integration Test**
```bash
# Test celotne integracije
python -m mia.core.hybrid_integration
```

### **End-to-End Test**
```bash
# Test launcher-ja
python mia_hybrid_launcher.py --mode adaptive --no-browser
```

## 📈 **Performance & Monitoring**

### **Statistike Sistema**
- **Request Statistics**: Skupno, uspešno, neuspešno
- **Mode Statistics**: Classic, hybrid, fallback aktivacije
- **Performance**: Cache hit ratio, povprečni čas procesiranja
- **Component Health**: Status vseh komponent

### **Monitoring**
- **Health Checks**: Avtomatsko preverjanje zdravja
- **Real-time Stats**: Posodabljanje v realnem času
- **Logging**: Strukturirano beleženje v datoteko
- **Error Tracking**: Sledenje napakam in recovery

## 🛠️ **Konfiguracija**

### **Environment Variables**
```bash
export MIA_DATA_DIR="/path/to/data"
export MIA_LOG_LEVEL="INFO"
export MIA_WEB_PORT="8000"
export MIA_MODE="hybrid_enhanced"
```

### **Configuration File**
```python
# config.py
LAUNCHER_CONFIG = {
    "mode": "hybrid_enhanced",
    "enable_web": True,
    "enable_monitoring": True,
    "web_port": 8000,
    "data_dir": "data"
}
```

## 🔒 **Varnost**

### **Varnostne Funkcionalnosti**
- **Input Validation**: Validacija vseh vnosov
- **Error Handling**: Comprehensive error handling
- **Graceful Shutdown**: Varen zaustavitev sistema
- **Data Protection**: Varovanje podatkov uporabnikov

### **Best Practices**
- Redni backup podatkov
- Monitoring sistema
- Posodabljanje odvisnosti
- Varno shranjevanje konfiguracije

## 🚨 **Troubleshooting**

### **Pogosti Problemi**

#### **1. Import Errors**
```bash
# Preverite Python path
export PYTHONPATH="${PYTHONPATH}:/path/to/Mia"

# Namestite manjkajoče odvisnosti
pip install -r requirements_hybrid.txt
```

#### **2. Web Server Issues**
```bash
# Preverite port
netstat -tulpn | grep :8000

# Uporabite drug port
python mia_hybrid_launcher.py --web-port 8080
```

#### **3. Memory Issues**
```bash
# Zmanjšajte cache size
# V konfiguraciji nastavite manjše vrednosti za cache_size
```

#### **4. Component Failures**
```bash
# Preverite loge
tail -f mia_hybrid.log

# Uporabite fallback mode
python mia_hybrid_launcher.py --mode classic
```

## 📚 **Dokumentacija**

### **API Reference**
- Podrobna dokumentacija vseh API-jev
- Primeri uporabe
- Response formati

### **Architecture Guide**
- Hibridna arhitektura
- Component interactions
- Data flow

### **Developer Guide**
- Razširjanje sistema
- Custom komponente
- Integration patterns

## 🤝 **Prispevanje**

### **Development Setup**
```bash
# Clone repository
git clone https://github.com/Lukifuki1/Mia.git
cd Mia

# Install development dependencies
pip install -r requirements_hybrid.txt
pip install -r requirements_dev.txt

# Run tests
pytest tests/
```

### **Code Style**
- Black formatting
- Type hints
- Comprehensive docstrings
- Error handling

## 📄 **Licenca**

Ta projekt je licenciran pod MIT licenco. Glej LICENSE datoteko za podrobnosti.

## 🎉 **Zaključek**

MIA Hybrid System predstavlja najnaprednejšo implementacijo hibridne umetne inteligence, ki združuje najboljše iz neural in symbolic pristopov. Sistem je zasnovan za produkcijsko uporabo z vsemi potrebnimi funkcionalnostmi za enterprise okolja.

**Ključne prednosti:**
- ✅ **100% Produkcijska koda** - brez TODO/demo/placeholder
- ✅ **Backward compatibility** - ohrani vse obstoječe funkcionalnosti
- ✅ **Enhanced capabilities** - dodaj napredne AI funkcionalnosti
- ✅ **Robust architecture** - zanesljiva in skalabilna arhitektura
- ✅ **Comprehensive monitoring** - popoln nadzor nad sistemom

---

**🚀 Pripravljen za produkcijo. Pripravljen za prihodnost AI.**