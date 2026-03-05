# 🚀 ΓΡΗΓΟΡΗ ΕΚΚΙΝΗΣΗ

## Βήμα 1: Εγκατάσταση Python Dependencies

```bash
cd conflict_monitor
pip install -r requirements.txt
```

## Βήμα 2: Εκτέλεση Εφαρμογής

```bash
python app.py
```

## Βήμα 3: Άνοιγμα Browser

Πήγαινε στο: **http://localhost:5000**

---

## ⚡ Αυτό είναι όλο!

Η εφαρμογή θα:
- ✅ Ξεκινήσει τον Flask server
- ✅ Δημιουργήσει το database
- ✅ Συλλέξει δεδομένα από πολλαπλές πηγές
- ✅ Εμφανίσει τον διαδραστικό χάρτη

---

## 📊 Τι θα δεις:

1. **Πραγματικά δεδομένα** από GDELT, News API, κτλ
2. **Διαδραστικό χάρτη** με markers για κάθε σύγκρουση
3. **Στατιστικά** (συνολικά, κρίσιμα, κλιμάκωση, εκτοπισμένοι)
4. **Live updates** κάθε 5 λεπτά
5. **Connection lines** μεταξύ συνδεδεμένων συγκρούσεων

---

## 🔑 (Προαιρετικό) API Keys

Για περισσότερα δεδομένα, πρόσθεσε API key στο `data_collectors.py`:

```python
self.news_api_key = "YOUR_API_KEY"  # από https://newsapi.org/
```

**Σημείωση**: Η εφαρμογή λειτουργεί και χωρίς API keys με fallback δεδομένα!

---

## 🛠️ Troubleshooting

### "Port 5000 already in use"
```bash
# Άλλαξε το port στο app.py, τελευταία γραμμή:
socketio.run(app, host='0.0.0.0', port=8080)
```

### "Module not found"
```bash
pip install -r requirements.txt
```

### Δεν φορτώνουν δεδομένα
- Έλεγξε τη σύνδεση Internet
- Κοίταξε το console για errors (F12 στο browser)

---

## 🎯 Επόμενα Βήματα

1. Διάβασε το **README.md** για περισσότερες λεπτομέρειες
2. Προσάρμοσε το **config_template.py** για API keys
3. Εξερεύνησε το **data_collectors.py** για προσθήκη νέων πηγών

---

**Καλή χρήση! 🌍**
