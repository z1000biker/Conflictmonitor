"""
OSINT Sources Collector - Κανάλια X, Telegram & News
"""

import requests
from bs4 import BeautifulSoup
import feedparser
from datetime import datetime
import threading
import time
import re
from typing import List, Dict
from duckduckgo_search import DDGS

# Greek military translator
GREEK_DICT = {
    'attack': 'επίθεση',
    'forces': 'δυνάμεις',
    'battle': 'μάχη',
    'killed': 'νεκροί',
    'wounded': 'τραυματίες',
    'destroyed': 'καταστράφηκε',
    'captured': 'αιχμαλωτίστηκε',
    'advance': 'προέλαση',
    'retreat': 'υποχώρηση',
    'shelling': 'βομβαρδισμός',
    'explosion': 'έκρηξη',
    'alert': 'συναγερμός',
    'war': 'πόλεμος',
    'conflict': 'σύγκρουση',
    'army': 'στρατός',
    'navy': 'ναυτικό',
    'air force': 'αεροπορία',
    'missile': 'πύραυλος',
    'drone': 'UAV',
    'tank': 'άρμα μάχης',
    'artillery': 'πυροβολικό',
    'breaking': 'ΕΚΤΑΚΤΟ',
    'update': 'ενημέρωση',
    'report': 'αναφορά',
    'claims': 'αναφορές',
    'confirmed': 'επιβεβαιωμένο',
    'unconfirmed': 'ανεπιβεβαιώτο',
    'civilian': 'άμαχοι',
    'infrastructure': 'υποδομές',
    'target': 'στόχος',
    'frontline': 'μέτωπο'
}

class OSINTCollector:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
    def translate_text(self, text: str) -> str:
        """
        Translates text to Greek using a dictionary-based approach.
        If text is already in Greek (detected by char range), returns it as is.
        """
        if not text:
            return ""
            
        # Check if already Greek (simple heuristic: contains Greek chars)
        if any('\u0370' <= c <= '\u03FF' for c in text):
            return text
            
        lower_text = text.lower()
        translated = text
        
        # Enhanced Dictionary for better context
        # (This is still basic, but better than nothing for English sources)
        replacements = {
            r'\bbreaking( news)?\b': 'ΕΚΤΑΚΤΟ',
            r'\bconflicts?\b': 'Σύγκρουση',
            r'\bwar\b': 'Πόλεμος',
            r'\battack(ed)?\b': 'Επίθεση',
            r'\bforces?\b': 'Δυνάμεις',
            r'\bmilitary\b': 'Στρατιωτική',
            r'\bkilled\b': 'Νεκροί',
            r'\bwounded\b': 'Τραυματίες',
            r'\bcasualties\b': 'Απώλειες',
            r'\bsoldiers?\b': 'Στρατιώτες',
            r'\bcivilians?\b': 'Άμαχοι',
            r'\btanks?\b': 'Άρματα Μάχης',
            r'\bmissiles?\b': 'Πύραυλοι',
            r'\bdrones?\b': 'UAVs',
            r'\bair\s?strikes?\b': 'Αεροπορικές Επιδρομές',
            r'\bdefen[sc]e\b': 'Άμυνα',
            r'\brussian?\b': 'Ρωσική',
            r'\bukrain(ian|e)\b': 'Ουκρανική',
            r'\bisrael(i)?\b': 'Ισραηλινή',
            r'\bhamas\b': 'Χαμάς',
            r'\bgaza\b': 'Γάζα',
            r'\breported\b': 'Αναφέρθηκε',
            r'\bclaims?\b': 'Ισχυρισμοί',
            r'\bcaptured\b': 'Καταλήφθηκε',
            r'\bdestroyed\b': 'Καταστράφηκε',
            r'\bfrontline\b': 'Μέτωπο',
            r'\bsector\b': 'Τομέας',
            r'\badvancing\b': 'Προελαύνουν',
            r'\bretreating\b': 'Υποχωρούν',
            r'\bexplosion\b': 'Έκρηξη',
            r'\bsiren(s)?\b': 'Σειρήνες',
            r'\balert\b': 'Συναγερμός'
        }
        
        for pattern, replacement in replacements.items():
            translated = re.sub(pattern, replacement, translated, flags=re.IGNORECASE)
            
        return translated



    def get_telegram_feed(self, channel: str) -> List[Dict]:
        """Scrape public Telegram channel preview"""
        try:
            url = f"https://t.me/s/{channel}"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                print(f"[!] Αποτυχία σύνδεσης στο Telegram: {channel}")
                return []
                
            soup = BeautifulSoup(response.content, 'html.parser')
            posts = soup.find_all('div', class_='tgme_widget_message_text')
            
            feed = []
            for post in posts[:10]:
                text = post.get_text(separator=' ', strip=True)
                # Cleanup common junk
                text = re.sub(r'http\S+', '', text).strip()
                
                if len(text) > 20:
                    greek_text = self.translate_text(text)
                    feed.append({
                        'source': f'Telegram (@{channel})',
                        'raw_text': text,
                        'text': greek_text,
                        'timestamp': datetime.now().isoformat(),
                        'type': 'telegram',
                        'url': url
                    })
            return feed
        except Exception as e:
            print(f"[!] Telegram Scraping Error ({channel}): {e}")
            return []

    def get_reddit_feed(self, subreddit: str) -> List[Dict]:
        """Get Reddit JSON feed (proxy for X/Twitter content)"""
        try:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit=10"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return []
                
            data = response.json()
            posts = data.get('data', {}).get('children', [])
            
            feed = []
            for post in posts:
                p_data = post.get('data', {})
                title = p_data.get('title', '')
                
                if 'repost' in title.lower() or len(title) < 10:
                    continue
                    
                greek_title = self.translate_text(title)
                
                feed.append({
                    'source': f'Reddit (r/{subreddit})',
                    'raw_text': title,
                    'text': greek_title,
                    'timestamp': datetime.fromtimestamp(p_data.get('created_utc')).isoformat(),
                    'type': 'reddit',
                    'url': f"https://reddit.com{p_data.get('permalink')}"
                })
            return feed
        except Exception as e:
            print(f"[!] Reddit Error ({subreddit}): {e}")
            return []

    def get_rss_news(self, feed_url: str, source_name: str) -> List[Dict]:
        """Get RSS News Feed"""
        try:
            feed = feedparser.parse(feed_url)
            
            posts = []
            for entry in feed.entries[:10]:
                title = entry.title
                greek_title = self.translate_text(title)
                
                posts.append({
                    'source': source_name,
                    'raw_text': title,
                    'text': greek_title,
                    'timestamp': datetime.now().isoformat(),
                    'type': 'news',
                    'url': entry.link
                })
            return posts
        except Exception as e:
            print(f"[!] RSS Error ({source_name}): {e}")
            return []

    def perform_deep_search(self, query: str) -> List[Dict]:
        """
        Conducts a deep, multi-stage search across high-value OSINT repositories
        and strategic news sites to find detailed intelligence.
        """
        if not query:
            return []
            
        # 1. High-Tier Strategic & NGO Domains
        intel_domains = [
            'acleddata.com', 'reliefweb.int', 'crisisgroup.org', 
            'understandingwar.org', 'bellingcat.com', 'csis.org', 
            'rusi.org', 'rand.org', 'oryxspioenkop.com', 'aljazeera.com',
            'reuters.com', 'apnews.com', 'isdp.eu', 'ecfr.eu'
        ]
        
        # 2. Comprehensive Query Strategy
        # Stage 1: Extreme Precision (Specific Domains)
        site_filter = " OR ".join([f"site:{d}" for d in intel_domains])
        
        # Stage 2: Broadened Intel & Strategic Keywords
        queries = [
            f'"{query}" (conflict OR war OR "military update" OR "situation report" OR "tactical map")',
            f'"{query}" ({site_filter})',
            f'"{query}" (battle OR offensive OR shelling OR "casualties reported")',
            # Greek Query for local sources
            f'"{query}" (σύγκρουση OR πόλεμος OR "πολεμικές επιχειρήσεις" OR "τακτική κατάσταση")'
        ]
        
        results = []
        try:
            with DDGS() as ddgs:
                for q in queries:
                    print(f"[*] Executing Intelligence Search: {q}")
                    try:
                        search_gen = ddgs.text(q, region='wt-wt', safesearch='off', max_results=10)
                        
                        for r in search_gen:
                            # Quality filter
                            if len(r.get('body', '')) < 50: continue
                            if any(res['url'] == r['href'] for res in results): continue
                            
                            results.append({
                                'source': f'Deep Intel ({r.get("href", "").split("//")[1].split("/")[0]})',
                                'raw_text': r.get('title', ''),
                                'text': self.translate_text(f"{r.get('title')}: {r.get('body')}"),
                                'timestamp': datetime.now().isoformat(),
                                'type': 'deep_search',
                                'url': r.get('href')
                            })
                            
                        if len(results) >= 8: break # Got sufficient depth
                    except Exception as sq_err:
                        print(f"Sub-query failed: {sq_err}")
                        continue
                        
                # 3. Global Emergency Fallback
                if len(results) < 3:
                    print(f"[*] Intelligence search thin, triggering global fallback for {query}")
                    fallback_q = f"latest {query} conflict military news situational analysis"
                    search_gen = ddgs.text(fallback_q, region='wt-wt', safesearch='off', max_results=10)
                    for r in search_gen:
                         results.append({
                            'source': 'Global Intelligence Network',
                            'raw_text': r.get('title', ''),
                            'text': self.translate_text(f"{r.get('title')}: {r.get('body')}"),
                            'timestamp': datetime.now().isoformat(),
                            'type': 'deep_search',
                            'url': r.get('href')
                        })

        except Exception as e:
            print(f"[!] Deep Search Error: {e}")
            
        return results[:10] # Return up to 10 best matches

    def get_youtube_feed(self, channel_id: str, name: str) -> List[Dict]:
        """Get YouTube RSS Feed"""
        try:
            url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
            return self.get_rss_news(url, f"YouTube ({name})")
        except Exception:
            return []

    def collect_all(self) -> List[Dict]:
        """Collect from all sources"""
        all_feeds = []
        
        # 1. Greek Telegram Channels (High Priority)
        greek_channels = [
            'polemikosantapokritis', 
            'infognomon',           
            'geostrategic',       
            'proelasi',             
            'defence_greece'        
        ]
        
        for ch in greek_channels:
            items = self.get_telegram_feed(ch)
            for item in items:
                item['source'] = f'Telegram (@{ch})' 
            all_feeds.extend(items)
            
        # 2. International Telegram (High Value / User Requested)
        intl_channels = [
            'molfar_global',   # Global Agency
            'osinttechnical',  # Technical/Verify
            'conflictwatcher', 
            'BellumActaNews',
            'cyb_detective',   # Cyber Detective
            'russian_osint',   # Russian OSINT Lab
            'osint_club',      # OSINT Club
            'project_omega_li',# Project Omega
            
            # X / Twitter Mirrors (User Requested)
            'sentdefender',    # OSINTdefender
            'liveuamap'        # Liveuamap
        ] 
        for ch in intl_channels:
            all_feeds.extend(self.get_telegram_feed(ch))
            
        # 3. Reddit (Selective)
        subreddits = ['ConflictNews', 'CombatFootage', 'Bellingcat']
        for sub in subreddits:
            all_feeds.extend(self.get_reddit_feed(sub))
            
        # 4. RSS Feeds (News, Investigations, Think Tanks)
        rss_feeds = [
            # Greek News
            ('https://www.defence-point.gr/feed', 'DefencePoint.gr'),
            ('https://www.militaire.gr/feed/', 'Militaire.gr'),
            ('https://www.ptisidiastima.com/feed/', 'Ptisi & Diastima'),
            
            # Investigations / Blogs
            ('https://www.bellingcat.com/feed/', 'Bellingcat'),
            ('https://gralhix.com/feed/', 'Sofia Santos (Gralhix)'),
            ('https://osintcurio.us/feed/', 'OSINT Curious'),
            ('https://osintfr.com/fr/feed/', 'OSINT-FR'),
            ('https://www.sans.org/blog/rss/', 'SANS OSINT'),
            ('https://osint.cavementech.com/feed/', 'CavemanTech OSINT'),
            ('https://chinese-military-aviation.blogspot.com/feeds/posts/default', 'Chinese Military Aviation'),
            
            # Technical & Methodology (X Sources)
            ('https://inteltechniques.com/blog/feed/', 'IntelTechniques (Michael Bazzell)'),
            ('https://www.maltego.com/blog/feed.xml', 'Maltego HQ'), # Probable
            ('https://blog.shodan.io/rss/', 'Shodan Blog'),
            ('https://www.osintcombine.com/blog-feed.xml', 'OSINT Combine'),
            ('https://liveuamap.com/feed', 'Liveuamap (RSS)'),

            # Think Tanks (Strategic)
            ('https://www.csis.org/rss/analysis', 'CSIS'),
            ('https://www.rand.org/pubs.xml', 'RAND Corp'),
            ('https://rusi.org/rss', 'RUSI'),
            ('https://www.brookings.edu/feed/', 'Brookings'),
            ('https://www.hudson.org/rss', 'Hudson Institute')
        ]
        for url, name in rss_feeds:
            all_feeds.extend(self.get_rss_news(url, name))
            
        # 5. YouTube Educational/Methodology
        youtube_channels = [
            ('UC0ZTPkdxlAKf-V33tqXwi3Q', 'OSINT Dojo'),
            ('UC_slP49u_fTebvYqK7YQJ4A', 'David Bombal'),
            ('UClcE-kVhqyiHCcjYwcpfj9w', 'LiveOverflow'), 
            ('UCy2eX5C_c9rUf1bF71a-6kQ', 'Bendobrown'),
            ('UCCgK7A_Yg4B7T8x-H1eZ4CQ', 'Perun (Strategy)'),
            ('UCXq1ESwQ3pEw02VpI439S4A', 'Anders Puck Nielsen'),
            ('UC_hqg81N9k0R6xna0aNGoPw', 'Gunners Shot'),
            ('UCAJtXb8W8eCjK3oK_T-bE1A', 'Österreichs Bundesheer'),
        ]
        for ch_id, name in youtube_channels:
            all_feeds.extend(self.get_youtube_feed(ch_id, name))

        return all_feeds

if __name__ == "__main__":
    # Test run
    collector = OSINTCollector()
    feeds = collector.collect_all()
    print(f"Collected {len(feeds)} items")
    for f in feeds[:3]:
        print(f"[{f['source']}] {f['text']}")
