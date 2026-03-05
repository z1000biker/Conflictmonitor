# 🌍 Παγκόσμιος Χάρτης Συγκρούσεων

**Real-time Conflict Monitoring System** - Σύστημα παρακολούθησης παγκόσμιων συγκρούσεων σε πραγματικό χρόνο με δεδομένα από πολλαπλές αξιόπιστες πηγές.

## 📋 Περιγραφή

Αυτή η εφαρμογή συλλέγει και παρουσιάζει δεδομένα για ενεργές συγκρούσεις παγκοσμίως από πολλαπλές πηγές:
- **GDELT Project** - Global Database of Events, Language, and Tone
- **ACLED** - Armed Conflict Location & Event Data Project  
- **News API** - Ειδησεογραφικά άρθρα σε πραγματικό χρόνο
- **Uppsala UCDP** - Uppsala Conflict Data Program
- **UN OCHA, UNHCR** - Δεδομένα ανθρωπιστικών κρίσεων

## ✨ Χαρακτηριστικά

- ✅ **Real-time updates** με WebSocket
- ✅ **Διαδραστικός χάρτης** με Leaflet
- ✅ **Πολλαπλές πηγές δεδομένων**
- ✅ **Επίπεδα απειλής** (Critical, High, Medium, Low)
- ✅ **Στατιστικά** (συγκρούσεις, θύματα, εκτοπισμένοι)
- ✅ **Connection lines** (proxy wars, arms flow, alliances)
- ✅ **Palantir-style UI** με σκούρο θέμα
- ✅ **Background data collection** κάθε 5 λεπτά
- ✅ **SQLite database** για ιστορικά δεδομένα

## 🚀 Εγκατάσταση

### Προαπαιτούμενα

- Python 3.8 ή νεότερο
- pip (Python package installer)

### Βήματα Εγκατάστασης

1. **Κλωνοποίηση ή download του project**
   ```bash
   cd conflictmonitor
   ```

2. **Δημιουργία virtual environment (προαιρετικό αλλά συνιστάται)**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Εγκατάσταση dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ρύθμιση API Keys (προαιρετικό)**
   
   Άνοιξε το `data_collectors.py` και πρόσθεσε τα API keys σου:
   
   ```python
   self.news_api_key = "YOUR_NEWS_API_KEY"  # από https://newsapi.org/
   ```
   
   **Σημείωση**: Η εφαρμογή λειτουργεί και χωρίς API keys με fallback δεδομένα.

## ▶️ Εκτέλεση

```bash
python app.py
```

Η εφαρμογή θα ξεκινήσει στο: **http://localhost:5000**

## 📊 Πηγές Δεδομένων

### 1. GDELT Project
- **URL**: https://www.gdeltproject.org/
- **Περιγραφή**: Global Knowledge Graph με realtime events
- **Χρήση**: Αυτόματη συλλογή (δεν απαιτεί API key)

### 2. News API
- **URL**: https://newsapi.org/
- **Περιγραφή**: Ειδησεογραφικά άρθρα από 80,000+ πηγές
- **Χρήση**: Χρειάζεται API key (δωρεάν για 100 requests/ημέρα)
- **Εγγραφή**: https://newsapi.org/register

### 3. ACLED (Simulated)
- **URL**: https://acleddata.com/
- **Περιγραφή**: Armed Conflict Location & Event Data
- **Χρήση**: Χρειάζεται εγγραφή για real data

### 4. Uppsala UCDP (Simulated)
- **URL**: https://ucdp.uu.se/
- **Περιγραφή**: Conflict Data από το Uppsala University
- **Χρήση**: Διαθέσιμο μέσω API

## 🎨 UI/UX Features

- **Dark Mode**: Palantir-inspired σκούρο θέμα
- **Animated Grid**: Κινούμενο background grid
- **Live Indicator**: Αναβοσβήνουσα ένδειξη live monitoring
- **Threat Colors**: 
  - 🔴 Critical (κόκκινο)
  - 🟠 High (πορτοκαλί)
  - 🟡 Medium (κίτρινο)
  - 🟢 Low (πράσινο)
- **Interactive Map**: Zoom, pan, click markers
- **Real-time Updates**: WebSocket push notifications
- **Responsive Design**: Λειτουργεί σε όλες τις συσκευές

## 📁 Δομή Project

```
conflict_monitor/
├── app.py                 # Main Flask application
├── data_collectors.py     # Data collection από πολλαπλές πηγές
├── database.py           # SQLite database management
├── requirements.txt      # Python dependencies
├── templates/
│   └── index.html       # HTML template
├── static/
│   ├── css/
│   └── js/
│       └── app.js       # Frontend JavaScript
└── conflicts.db         # SQLite database (δημιουργείται αυτόματα)
```

## ⚙️ Ρυθμίσεις

### Update Interval

Στο `app.py`, γραμμή 19:
```python
update_interval = 300  # 5 λεπτά (σε δευτερόλεπτα)
```

### Database Path

Στο `app.py`, γραμμή 27:
```python
db = Database('conflicts.db')  # Αλλαγή path αν χρειάζεται
```

## 🔧 Troubleshooting

### Port 5000 κατειλημμένο
```bash
# Αλλαγή port στο app.py, τελευταία γραμμή:
socketio.run(app, host='0.0.0.0', port=8080, debug=True)
```

### Σφάλματα εγκατάστασης
```bash
# Αν υπάρχουν προβλήματα με eventlet:
pip install --upgrade eventlet

# Αν υπάρχουν προβλήματα με flask-socketio:
pip install --upgrade flask-socketio python-socketio
```

### Δεν φορτώνουν δεδομένα
1. Έλεγξε τη σύνδεση στο Internet
2. Έλεγξε το console για errors: `http://localhost:5000` → F12
3. Έλεγξε τα logs στο terminal που τρέχει η εφαρμογή

## 📈 Επεκτάσεις

### Προσθήκη νέας πηγής δεδομένων

Στο `data_collectors.py`, πρόσθεσε νέα μέθοδο:

```python
def collect_from_new_source(self) -> List[Dict]:
    conflicts = []
    # Κώδικας συλλογής δεδομένων
    return conflicts
```

Και κάλεσέ τη από το `collect_all_sources()`.

### Προσθήκη νέων regions

Στο `data_collectors.py`, στο `self.regions` dictionary:

```python
self.regions = {
    'NewCountry': {'lat': 0.0, 'lng': 0.0, 'region': 'Region Name'},
    # ...
}
```

## 🔐 Security

⚠️ **Προσοχή**: Μην κοινοποιήσετε API keys σε public repositories!

Χρησιμοποίησε environment variables:
```python
import os
self.news_api_key = os.getenv('NEWS_API_KEY', 'default_key')
```

## 📝 License

MIT License - Ελεύθερο για χρήση και τροποποίηση

## 🤝 Συνεισφορά

Contributions are welcome! 

1. Fork το project
2. Δημιούργησε feature branch
3. Commit τις αλλαγές σου
4. Push στο branch
5. Άνοιξε Pull Request

## 📞 Support

Για ερωτήσεις και προβλήματα, άνοιξε issue στο GitHub ή επικοινώνησε.

## 🙏 Credits

- **Maps**: OpenStreetMap, CartoDB
- **Icons**: Lucide Icons
- **Fonts**: Google Fonts (Rajdhani, Orbitron)
- **Data Sources**: GDELT, ACLED, News API, Uppsala UCDP

---

**Φτιαγμένο με ❤️ για παρακολούθηση παγκόσμιων συγκρούσεων**
