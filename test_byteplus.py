#!/usr/bin/env python3
"""
BytePlus ModelArk — Quick Test Script
Endpoint: (set via BYTEPLUS_ENDPOINT env var)
"""

import os, json, time

ENDPOINT_ID = os.environ.get("BYTEPLUS_ENDPOINT", "")  # set trong .env
BASE_URL = "https://ark.ap-southeast.bytepluses.com/api/v3"
API_KEY = os.environ.get("BYTEPLUS_API_KEY", "")  # set trong .env hoặc env var

def test_basic():
    """Test gọi đơn giản"""
    try:
        from volcenginesdkarkruntime import Ark
        client = Ark(base_url=BASE_URL, api_key=API_KEY)
        
        print("📡 Gọi BytePlus ModelArk...")
        t0 = time.time()
        resp = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=[{"role": "user", "content": "Say hello in Vietnamese in one sentence."}],
            max_tokens=100
        )
        elapsed = time.time() - t0
        
        print(f"✅ SUCCESS! ({elapsed:.1f}s)")
        print(f"📝 Response: {resp.choices[0].message.content}")
        print(f"📊 Tokens: {resp.usage.prompt_tokens} in / {resp.usage.completion_tokens} out")
        return True
        
    except ImportError:
        print("⚠️  volcenginesdkarkruntime chưa cài. Chạy: pip install volcenginesdkarkruntime")
        return test_fallback_requests()
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_fallback_requests():
    """Test bằng requests thuần (không cần SDK)"""
    import urllib.request
    
    if not API_KEY:
        print("❌ Chưa có API_KEY. Set: export BYTEPLUS_API_KEY='your_key_here'")
        return False
    
    payload = {
        "model": ENDPOINT_ID,
        "messages": [{"role": "user", "content": "Say hello in Vietnamese in one sentence."}],
        "max_tokens": 100
    }
    req = urllib.request.Request(
        f"{BASE_URL}/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {API_KEY}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            result = json.loads(r.read())
            content = result["choices"][0]["message"]["content"]
            print(f"✅ SUCCESS!")
            print(f"📝 Response: {content}")
            return True
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP {e.code}: {e.read().decode()}")
        return False

def test_campaign_prompt():
    """Test prompt thực tế cho BP-01"""
    try:
        from volcenginesdkarkruntime import Ark
        client = Ark(base_url=BASE_URL, api_key=API_KEY)
        
        system = """You are a cross-border e-commerce campaign strategist.
Given a product and target market, generate a structured campaign plan.
Always respond in valid JSON."""
        
        user = """Product: Graphic T-shirt (POD, $29)
Target market: US (18-34, fashion-forward)
Budget: $500
Goal: Conversion
Duration: 2 weeks

Generate a campaign plan with: target_audience, channel_strategy, ad_copy, budget_breakdown, predicted_metrics"""
        
        print("\n📡 Test Campaign Prompt...")
        t0 = time.time()
        resp = client.chat.completions.create(
            model=ENDPOINT_ID,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user}
            ],
            max_tokens=800,
            temperature=0.7
        )
        elapsed = time.time() - t0
        
        print(f"✅ Campaign prompt OK! ({elapsed:.1f}s)")
        print(resp.choices[0].message.content[:500] + "...")
        return True
    except Exception as e:
        print(f"❌ {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print(f"🔑 API Key: {'SET ✅' if API_KEY else 'NOT SET ❌'}")
    print(f"🎯 Endpoint: {ENDPOINT_ID}")
    print("=" * 50)
    
    ok = test_basic()
    if ok:
        test_campaign_prompt()
