import requests
import time
import threading
from datetime import datetime
import json
import os
from fastapi import FastAPI
import uvicorn
import asyncio

app = FastAPI()

class WebsitePinger:
    def __init__(self, interval_minutes=13, config_file="websites.json"):
        self.interval = interval_minutes * 60
        self.config_file = config_file
        self.websites = self.load_websites()
        self.is_running = False
        self.ping_task = None
        
    def load_websites(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return [
                {"url": "https://programmers-union.onrender.com", "method": "GET"},
                {"url": "https://chatbot-nexusai.onrender.com", "method": "GET"},
                {"url": "https://abdulaziz-mohammed-alqudimi.onrender.com", "method": "GET"},
            ]
    
    def save_websites(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.websites, f, indent=2, ensure_ascii=False)
    
    def send_ping(self, website_config):
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
            time.sleep(0.5)
        
        for thread in threads:
            thread.join()
    
    async def start_pinging(self):
        self.is_running = True
        print(f"بدأت خدمة الإرسال الدوري كل {self.interval/60} دقائق")
        
        while self.is_running:
            self.ping_all()
            
            for _ in range(self.interval):
                if not self.is_running:
                    break
                await asyncio.sleep(1)
    
    def stop_pinging(self):
        self.is_running = False
        print("إيقاف الخدمة...")

pinger = WebsitePinger(interval_minutes=3)

@app.get("/")
async def root():
    html_content = f"""
    <html>
        <head>
            <title>Website Pinger</title>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                .container {{ max-width: 800px; margin: 0 auto; }}
                .website {{ padding: 10px; margin: 5px 0; background: #f5f5f5; }}
                .status {{ float: right; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Website Pinger Service</h1>
                <p>الحالة: <strong>{'🟢 قيد التشغيل' if pinger.is_running else '🔴 متوقف'}</strong></p>
                <p>الفاصل الزمني: {pinger.interval/60} دقائق</p>
                
                <h2>المواقع المستهدفة:</h2>
                {"".join(f'<div class="website">{site["url"]} <span class="status">({site.get("method", "GET")})</span></div>' for site in pinger.websites)}
                
                <br>
                <div>
                    <a href="/start" style="background: green; color: white; padding: 10px; text-decoration: none; margin: 5px;">تشغيل الخدمة</a>
                    <a href="/stop" style="background: red; color: white; padding: 10px; text-decoration: none; margin: 5px;">إيقاف الخدمة</a>
                </div>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/start")
async def start_service():
    if not pinger.is_running:
        pinger.ping_task = asyncio.create_task(pinger.start_pinging())
        return {"status": "success", "message": "تم تشغيل الخدمة"}
    else:
        return {"status": "info", "message": "الخدمة قيد التشغيل بالفعل"}

@app.get("/stop")
async def stop_service():
    if pinger.is_running:
        pinger.stop_pinging()
        if pinger.ping_task:
            pinger.ping_task.cancel()
        return {"status": "success", "message": "تم إيقاف الخدمة"}
    else:
        return {"status": "info", "message": "الخدمة متوقفة بالفعل"}

from fastapi.responses import HTMLResponse

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
