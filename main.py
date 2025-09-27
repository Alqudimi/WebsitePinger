import requests
import time
import threading
from datetime import datetime
import json
import os

class WebsitePinger:
    def __init__(self, interval_minutes=13, config_file="websites.json"):
        self.interval = interval_minutes * 60  
        self.config_file = config_file
        self.websites = self.load_websites()
        self.is_running = True
        
    def load_websites(self):
        """تحميل قائمة المواقع من ملف JSON أو استخدام القائمة الافتراضية"""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            
            return [
                {"url": "https://programmers-union.onrender.com", "method": "GET"},
              #  {"url": "https://jsonplaceholder.typicode.com/posts/1", "method": "GET"},
               # {"url": "https://api.github.com", "method": "GET"},
            ]
    
    def save_websites(self):
        """حفظ قائمة المواقع إلى ملف JSON"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.websites, f, indent=2, ensure_ascii=False)
    
    def send_ping(self, website_config):
        """إرسال طلب إلى موقع معين"""
        url = website_config["url"]
        method = website_config.get("method", "GET")
        
        try:
            start_time = time.time()
            
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, timeout=30)
            else:
                response = requests.request(method, url, timeout=30)
            
            end_time = time.time()
            duration = round((end_time - start_time) * 1000, 2)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            if 200 <= response.status_code < 300:
                print(f"{timestamp} ✅ {url} - {response.status_code} ({duration}ms)")
            else:
                print(f"{timestamp} ⚠️  {url} - {response.status_code} ({duration}ms)")
                
        except Exception as e:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"{timestamp} ❌ {url} - خطأ: {e}")
    
    def ping_all(self):
        
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] إرسال الطلبات الدورية...")
        
        threads = []
        for website in self.websites:
            thread = threading.Thread(target=self.send_ping, args=(website,))
            threads.append(thread)
            thread.start()
            time.sleep(0.5)  # فواصل صغيرة بين بدء الخيوط
        
        
        for thread in threads:
            thread.join()
    
    def start(self):
        """بدء الخدمة"""
        print(f"بدأت خدمة الإرسال الدوري كل {self.interval/60} دقائق")
        print("اضغط على Ctrl+C لإيقاف الخدمة")
        
        try:
            while self.is_running:
                self.ping_all()
                
                # انتظار الفاصل الزمني
                for _ in range(self.interval):
                    if not self.is_running:
                        break
                    time.sleep(1)
                    
        except KeyboardInterrupt:
            print("\nإيقاف الخدمة...")
            self.stop()
    
    def stop(self):
        """إيقاف الخدمة"""
        self.is_running = False



pinger = WebsitePinger(interval_minutes=13)
    
pinger.start()
