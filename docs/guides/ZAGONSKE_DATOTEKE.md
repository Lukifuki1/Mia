# 🚀 ZAGONSKE DATOTEKE ZA MIA ENTERPRISE AGI

## 📍 **GLAVNE ZAGONSKE DATOTEKE:**

### **1. 💬 CHAT INTERFACE (PRIPOROČENO)**
```bash
python mia_chat_interface.py
```
- **Lokacija:** `/mia_chat_interface.py`
- **Port:** 12001
- **Opis:** Glavni chat vmesnik z WebSocket podporo
- **URL:** http://localhost:12001

### **2. 🚀 BOOTSTRAP LAUNCHER**
```bash
python mia_bootstrap.py
```
- **Lokacija:** `/mia_bootstrap.py`
- **Opis:** Glavni bootstrap sistem za zagon MIA
- **Funkcija:** Inicializacija vseh modulov

### **3. 💼 ENTERPRISE LAUNCHER**
```bash
python mia_enterprise_launcher.py
```
- **Lokacija:** `/mia_enterprise_launcher.py`
- **Opis:** Enterprise verzija z naprednimi funkcionalnostmi
- **Funkcije:** Compliance, audit, enterprise varnost

### **4. 🌐 WEB LAUNCHER**
```bash
python mia_web_launcher.py
```
- **Lokacija:** `/mia_web_launcher.py`
- **Opis:** Web dashboard z analitiko
- **Port:** 8080
- **URL:** http://localhost:8080

### **5. 🔧 GLAVNI LAUNCHER**
```bash
python mia_main.py
```
- **Lokacija:** `/mia_main.py`
- **Opis:** Osnovni launcher
- **Funkcija:** Enostaven zagon sistema

### **6. ⚡ HITRI ZAGON**
```bash
python run_mia.py
```
- **Lokacija:** `/run_mia.py`
- **Opis:** Hitri zagon z osnovnimi nastavitvami

---

## 🔧 **BOOTSTRAP DATOTEKE:**

### **7. 🥾 BOOTSTRAP CORE**
```bash
python bootstrap/mia_boot.py
```
- **Lokacija:** `/bootstrap/mia_boot.py`
- **Opis:** Jedro bootstrap sistema

---

## 🧪 **TESTNE DATOTEKE:**

### **8. 🧪 SISTEM TESTI**
```bash
python test_mia.py
```
- **Lokacija:** `/test_mia.py`
- **Opis:** Osnovni sistem testi

### **9. 🏃 ZAŽENI VSE TESTE**
```bash
python run_all_tests.py
```
- **Lokacija:** `/run_all_tests.py`
- **Opis:** Zažene vse teste v sistemu

---

## 🖥️ **DESKTOP APLIKACIJA:**

### **10. 🖥️ DESKTOP MAIN**
```bash
cd desktop
npm install
npm start
```
- **Lokacija:** `/desktop/main.js`
- **Opis:** Electron desktop aplikacija

---

## 📋 **PRIPOROČEN VRSTNI RED ZAGONA:**

### **PRVA UPORABA:**
1. **Preverite odvisnosti:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Zaženite bootstrap:**
   ```bash
   python mia_bootstrap.py
   ```

3. **Zaženite chat interface:**
   ```bash
   python mia_chat_interface.py
   ```

4. **Odprite browser:**
   ```
   http://localhost:12001
   ```

### **VSAKODNEVNA UPORABA:**
```bash
python mia_chat_interface.py
```

### **ENTERPRISE UPORABA:**
```bash
python mia_enterprise_launcher.py
```

### **RAZVOJ IN TESTIRANJE:**
```bash
python run_all_tests.py
python mia_web_launcher.py  # Za dashboard
```

---

## ⚙️ **KONFIGURACIJA:**

### **Glavne konfiguracijske datoteke:**
- `mia_config.yaml` - Glavna konfiguracija
- `modules.toml` - Moduli
- `settings.json` - Nastavitve
- `requirements.txt` - Python odvisnosti

### **Podatkovne mape:**
- `mia_data/` - Podatki sistema
- `mia/data/` - Konfiguracijski podatki
- `cache/` - Predpomnilnik

---

## 🎯 **HITRI START:**

```bash
# 1. Klonirajte repozitorij
git clone https://github.com/Lukifuki1/Mia.git
cd Mia

# 2. Namestite odvisnosti
pip install -r requirements.txt

# 3. Zaženite MIA
python mia_chat_interface.py

# 4. Odprite browser
# http://localhost:12001
```

---

## 🔍 **PREVERJANJE DELOVANJA:**

```bash
# Preverite ali MIA deluje
curl http://localhost:12001/health

# Preverite status
python -c "import mia_bootstrap; print('MIA je pripravljena!')"
```

---

## 📞 **POMOČ:**

Če imate težave z zagonom:
1. Preverite `requirements.txt`
2. Preverite `mia_config.yaml`
3. Zaženite `python test_mia.py`
4. Preverite loge v `chat_server.log`