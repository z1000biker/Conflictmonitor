"""
Παγκόσμιος Χάρτης Συγκρούσεων - Real-time Conflict Monitoring
Main Application File
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import threading
import time
from datetime import datetime
from data_collectors import ConflictDataCollector
from database import Database
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

from osint_sources import OSINTCollector

# Initialize collectors
db = Database()
collector_db = ConflictDataCollector(db)
osint_collector = OSINTCollector()

# Global state
current_conflicts = []
live_feed = []

def background_osint_collection():
    """Background thread για συλλογή OSINT feeds"""
    global live_feed
    while True:
        try:
            print(f"[{datetime.now()}] Συλλογή νέων δεδομένων OSINT...")
            feeds = osint_collector.collect_all()
            
            if feeds:
                latest = sorted(feeds, key=lambda x: x.get('timestamp', ''), reverse=True)[:100] # Increase to 100 for more depth
                live_feed = latest
                
                # Distribution stats for log
                sources_found = {}
                for it in latest:
                    s = it.get('source', 'Unknown')
                    sources_found[s] = sources_found.get(s, 0) + 1
                    
                print(f"✓ LIVE FEED UPDATED: {len(latest)} items from {len(sources_found)} sources.")
                for s, count in sources_found.items():
                    print(f"  - {s}: {count} items")
                
                # Push to clients
                socketio.emit('live_feed_update', {'feed': latest})
            else:
                print("! Καμία νέα εγγραφή OSINT (Check connection/sources)")
                
        except Exception as e:
            print(f"✗ CRITICAL OSINT ERROR: {e}")
            import traceback
            traceback.print_exc()
            
        socketio.sleep(300) # 5 mins

@app.route('/api/live_feed')
def get_live_feed():
    """Ζωντανή ροή δεδομένων από X/Telegram/News"""
    return jsonify({'feed': live_feed})


def background_data_collection():
    """Background thread για συλλογή δεδομένων σε real-time"""
    global current_conflicts
    
    while True:
        try:
            print(f"[{datetime.now()}] Συλλογή νέων δεδομένων...")
            
            # Συλλογή από όλες τις πηγές
            conflicts = collector_db.collect_all_sources()
            current_conflicts = conflicts
            
            # Αποθήκευση στη βάση
            db.save_conflicts(conflicts)
            
            # Αποστολή updates σε όλους τους συνδεδεμένους clients
            socketio.emit('conflict_update', {
                'conflicts': conflicts,
                'timestamp': datetime.now().isoformat(),
                'count': len(conflicts)
            })
            
            print(f"✓ Ενημερώθηκαν {len(conflicts)} συγκρούσεις")
            
        except Exception as e:
            print(f"✗ Σφάλμα στη συλλογή δεδομένων: {e}")
        
        socketio.sleep(300)

@app.route('/')
def index():
    """Κύρια σελίδα"""
    return render_template('index.html')


@app.route('/api/conflicts')
def get_conflicts():
    """API endpoint για λήψη τρεχουσών συγκρούσεων"""
    if not current_conflicts:
        # Load from database if not in memory
        conflicts = db.get_recent_conflicts()
    else:
        conflicts = current_conflicts
    
    stats = calculate_stats(conflicts)
    
    return jsonify({
        'conflicts': conflicts,
        'stats': stats,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/conflict/<int:conflict_id>')
def get_conflict_details(conflict_id):
    """Λεπτομέρειες συγκεκριμένης σύγκρουσης"""
    conflict = db.get_conflict_by_id(conflict_id)
    return jsonify(conflict)


@app.route('/api/stats')
def get_statistics():
    """Γενικά στατιστικά"""
    conflicts = current_conflicts if current_conflicts else db.get_recent_conflicts()
    stats = calculate_stats(conflicts)
    return jsonify(stats)


@app.route('/api/timeline/<conflict_name>')
def get_conflict_timeline(conflict_name):
    """Χρονολόγιο συγκεκριμένης σύγκρουσης"""
    timeline = db.get_conflict_timeline(conflict_name)
    return jsonify(timeline)


@app.route('/api/report/<conflict_location>')
def get_conflict_report(conflict_location):
    """Δημιουργία πλήρους αναφοράς για μια σύγκρουση"""
    # Find conflict in current memory
    conflict = next((c for c in current_conflicts if c.get('location') == conflict_location), None)
    
    if not conflict:
        return jsonify({'error': 'Conflict not found'}), 404
        
    relevant_news = []
    
    # Get keywords for this location from data_collectors config
    region_info = collector_db.regions.get(conflict_location)
    keywords = region_info.get('aliases', []) if region_info else [conflict_location.lower()]
    
    # Filter live feed using expanded keywords
    for item in live_feed:
        text = item.get('text', '').lower()
        if any(kw in text for kw in keywords):
            relevant_news.append(item)
            
    # Perform Deep Search (Active OSINT)
    try:
        # Use first keyword or location for search query
        search_query = keywords[0] if keywords else conflict_location
        print(f"Conducting deep search for: {search_query}...")
        deep_results = osint_collector.perform_deep_search(search_query)
        if deep_results:
            relevant_news.extend(deep_results)
            print(f"Found {len(deep_results)} deep search items.")
    except Exception as e:
        print(f"Deep search failed: {e}")

    # Add to conflict data temporarily for report generation
    conflict['latest_news'] = relevant_news
    
    report = collector_db.generate_greek_report(conflict)
    return jsonify({'report': report})


@app.route('/api/connections')
def get_connections():
    """Συνδέσεις μεταξύ συγκρούσεων (proxy wars, arms flow, κτλ)"""
    connections = collector_db.analyze_connections(current_conflicts)
    return jsonify(connections)

def calculate_stats(conflicts):
    """Υπολογισμός στατιστικών"""
    if not conflicts:
        return {
            'total': 0, 'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 
            'escalating': 0, 'total_casualties': 0, 'total_displaced': 0
        }
    
    stats = {
        'total': len(conflicts),
        'critical': sum(1 for c in conflicts if c.get('threat_level') == 'critical'),
        'high': sum(1 for c in conflicts if c.get('threat_level') == 'high'),
        'medium': sum(1 for c in conflicts if c.get('threat_level') == 'medium'),
        'low': sum(1 for c in conflicts if c.get('threat_level') == 'low'),
        'escalating': sum(1 for c in conflicts if c.get('status') == 'escalating'),
        'total_casualties': sum((c.get('casualties') or 0) for c in conflicts),
        'total_displaced': sum((c.get('displaced') or 0) for c in conflicts)
    }
    return stats

def start_background_collection():
    """Εκκίνηση background threads"""
    socketio.start_background_task(background_data_collection)
    socketio.start_background_task(background_osint_collection)
    print("✓ Background data & OSINT collection ξεκίνησαν")

if __name__ == '__main__':
    # Initialize database
    db.initialize()
    
    print("\n" + "="*60)
    print("🚀 ΕΚΚΙΝΗΣΗ ΣΥΣΤΗΜΑΤΟΣ ΠΑΡΑΚΟΛΟΥΘΗΣΗΣ")
    
    # Αρχική συλλογή δεδομένων (Synchronous for stability)
    print("1. Φόρτωση δεδομένων συγκρούσεων...")
    try:
        initial_data = collector_db.collect_all_sources()
        if not initial_data:
             print("! External APIs failed, forcing fallback...")
             initial_data = collector_db.get_fallback_data()
        
        current_conflicts = initial_data
        db.save_conflicts(initial_data)
        print(f"✓ Φορτώθηκαν {len(initial_data)} συγκρούσεις")
    except Exception as e:
        print(f"✗ Error loading conflicts: {e}")
        current_conflicts = collector_db.get_fallback_data()

    # Αρχική συλλογή OSINT (Synchronous)
    print("2. Φόρτωση OSINT Feeds (Αυτό μπορεί να πάρει λίγο χρόνο)...")
    try:
        initial_feed = osint_collector.collect_all()
        if initial_feed:
            live_feed = sorted(initial_feed, key=lambda x: x.get('timestamp', ''), reverse=True)[:50]
            print(f"✓ Φορτώθηκαν {len(live_feed)} αρχικές εγγραφές OSINT")
        else:
            print("! Δεν βρέθηκαν αρχικές εγγραφές OSINT")
    except Exception as e:
         print(f"✗ Error loading OSINT: {e}")

    # Εκκίνηση background collection
    print("3. Εκκίνηση Background Threads...")
    start_background_collection()
    
    # Εκκίνηση Flask server
    print("="*60)
    print("🌍 Η εφαρμογή τρέχει στο: http://localhost:5000")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
