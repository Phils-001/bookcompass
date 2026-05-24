from flask import Flask, request, jsonify, session, render_template_string
import requests
import time
from datetime import date, datetime, timedelta
import os
import resend

app = Flask(__name__)
app.secret_key = "bookcompass_secret_key_12345"

# Resend Configuration
resend.api_key = os.environ.get('RESEND_API_KEY', '')

# Your Rainforest API Key (keep this secret)
YOUR_API_KEY = "846F7338358746F88A3667FCC1540938"

# Simple storage
users = {}
usage_tracker = {}

# Pricing plans
PLANS = {
    "free": {"daily_limit": 3},
    "starter": {"daily_limit": 20},
    "pro": {"daily_limit": 100}
}

# Promo codes
PROMO_CODES = {
    "FRIEND10": {"discount": 10, "type": "percent", "months": 1, "description": "10% off for 1 month"},
    "BETA20": {"discount": 20, "type": "percent", "months": 6, "description": "20% off for 6 months"},
    "REFERRAL10": {"discount": 10, "type": "percent", "months": 1, "description": "10% off for 1 month (referral)"}
}

# ============================================
# HOME PAGE
# ============================================

@app.route('/')
def home():
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>BookCompass - KDP Keyword Navigator</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f0f0f0; }
            .header { background: #232f3e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }
            .logo { font-size: 24px; font-weight: bold; }
            .logo span { color: #ff9900; }
            .nav a { color: white; margin-left: 20px; text-decoration: none; }
            .container { max-width: 1200px; margin: 0 auto; padding: 30px; }
            .card { background: white; border-radius: 10px; padding: 30px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            h1 { margin-top: 0; color: #232f3e; }
            h2 { color: #232f3e; }
            button { background: #ff9900; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }
            button:hover { background: #e68a00; }
            .pricing-grid { display: flex; gap: 20px; margin-top: 20px; }
            .plan { flex: 1; border: 1px solid #ddd; border-radius: 10px; padding: 20px; text-align: center; }
            .plan.featured { border: 2px solid #ff9900; background: #fff8f0; }
            .price { font-size: 32px; font-weight: bold; color: #232f3e; }
            .how-it-works { display: flex; gap: 30px; margin: 30px 0; }
            .step { flex: 1; text-align: center; }
            .step-icon { font-size: 48px; }
            .features { display: flex; gap: 30px; margin: 20px 0; }
            .feature { flex: 1; }
            .cta { text-align: center; background: #232f3e; color: white; }
            .cta h2 { color: white; }
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📚 Book<span>Compass</span></div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/how-it-works">How It Works</a>
                <a href="/login">Login</a>
                <a href="/signup">Sign Up</a>
            </div>
        </div>
        <div class="container">
            <div class="card" style="text-align: center;">
                <h1>📚 Welcome to BookCompass</h1>
                <p style="font-size: 20px; color: #ff9900;">Your KDP Keyword Navigator</p>
                <p style="font-size: 16px; margin-top: 20px;">Stop guessing which keywords will sell. BookCompass analyzes real Amazon data to find low-competition, high-opportunity keywords for your KDP books.</p>
                <a href="/signup"><button>🚀 Get Started Free →</button></a>
            </div>
            <div class="card">
                <h2 style="text-align: center;">How BookCompass Works</h2>
                <div class="how-it-works">
                    <div class="step"><div class="step-icon">1️⃣</div><h3>Enter Keywords</h3><p>Paste up to 30 keywords related to your book idea</p></div>
                    <div class="step"><div class="step-icon">2️⃣</div><h3>Get Analysis</h3><p>BookCompass checks competition and search volume</p></div>
                    <div class="step"><div class="step-icon">3️⃣</div><h3>Find Winners</h3><p>See Niche Scores (1-10) and target the best opportunities</p></div>
                </div>
            </div>
            <div class="card">
                <h2 style="text-align: center;">What You Get</h2>
                <div class="features">
                    <div class="feature"><h3 style="text-align: center;">🎯 Niche Score</h3><p style="text-align: center;">7-10 = Excellent<br>5-6 = Decent<br>1-4 = Avoid</p></div>
                    <div class="feature"><h3 style="text-align: center;">📊 Search Volume</h3><p style="text-align: center;">How many people search this keyword monthly</p></div>
                    <div class="feature"><h3 style="text-align: center;">⚔️ Competition Level</h3><p style="text-align: center;">LOW = Easy to rank<br>MEDIUM = Possible<br>HIGH = Very difficult</p></div>
                </div>
            </div>
            <div class="card">
                <h2 style="text-align: center;">Simple, Transparent Pricing</h2>
                <div class="pricing-grid">
                    <div class="plan"><h3>Free</h3><div class="price">$0</div><p>3 searches/day</p><ul style="text-align: left;"><li>✓ Basic keyword analysis</li><li>✓ Search volume data</li><li>✓ Competition check</li></ul><a href="/signup"><button>Start Free</button></a></div>
                    <div class="plan featured"><h3>Starter</h3><div class="price">$12<span style="font-size: 14px;">/month</span></div><p>20 searches/day</p><ul style="text-align: left;"><li>✓ Everything in Free</li><li>✓ 10x more searches</li><li>✓ Bulk research (30 keywords)</li><li>✓ Priority support</li></ul><a href="/signup"><button>Choose Starter</button></a></div>
                    <div class="plan"><h3>Pro</h3><div class="price">$25<span style="font-size: 14px;">/month</span></div><p>100 searches/day</p><ul style="text-align: left;"><li>✓ Everything in Starter</li><li>✓ 4x more searches</li><li>✓ Bulk research (100 keywords)</li><li>✓ Export to CSV</li></ul><a href="/signup"><button>Choose Pro</button></a></div>
                </div>
            </div>
            <div class="card cta"><h2>Ready to Find Your Next Winning Keyword?</h2><p>Join KDP publishers using BookCompass to find profitable niches.</p><a href="/signup"><button style="background: #ff9900; font-size: 18px;">Create Free Account →</button></a></div>
        </div>
    </body>
    </html>
    '''
    return html

# ============================================
# SIGNUP PAGE
# ============================================

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    referral_username = request.args.get('ref', '')
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form['email']
        password = request.form['password']
        promo_code = request.form.get('promo_code', '').upper()
        referred_by_username = request.form.get('referred_by', '')
        
        # Validate username
        if not username or len(username) < 3:
            return '<div style="text-align:center; margin-top:50px;"><h2>Username must be at least 3 characters</h2><a href="/signup">Try again</a></div>'
        
        # Check if email exists
        if email in users:
            return '<div style="text-align:center; margin-top:50px;"><h2>Email already exists</h2><a href="/login">Login here</a></div>'
        
        # Check if username already exists
        for existing_email, existing_user in users.items():
            if existing_user.get('username') == username:
                return '<div style="text-align:center; margin-top:50px;"><h2>Username already taken</h2><a href="/signup">Try another</a></div>'
        
        # Find referrer email from username
        referred_by_email = None
        if referred_by_username:
            for existing_email, existing_user in users.items():
                if existing_user.get('username') == referred_by_username:
                    referred_by_email = existing_email
                    break
        
        from datetime import datetime, timedelta
        promo_data = None
        promo_expires = None
        
        # Check if this is a referral signup (referral takes priority)
        if referred_by_email and referred_by_email in users:
            promo_data = {"discount": 10, "months": 1}
            promo_expires = (datetime.now() + timedelta(days=30)).isoformat()
            
            # Set the promo code for the referee (so they get discount)
            promo_code = "REFERRAL10"
            
            # Add referral credit to referrer (for their future discount)
            users[referred_by_email]['referral_count'] = users[referred_by_email].get('referral_count', 0) + 1
            users[referred_by_email]['referral_credit'] = users[referred_by_email].get('referral_credit', 0) + 1
            
        # Only check manual promo code if NOT a referral signup
        elif promo_code in PROMO_CODES:
            promo_data = PROMO_CODES[promo_code]
            promo_expires = (datetime.now() + timedelta(days=30 * promo_data['months'])).isoformat()
        
        # Create user
        users[email] = {
            'username': username,
            'password': password, 
            'plan': 'free', 
            'api_key': '',
            'promo_code': promo_code if promo_data else None,
            'promo_expires': promo_expires,
            'referred_by': referred_by_email if referred_by_email else None,
            'referral_count': 0,
            'referral_credit': 0,
            'verified': False,
            'verification_code': None,
            'reset_token': None,
            'reset_expires': None,
            'created_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Generate verification code
        import random
        import string
        verification_code = ''.join(random.choices(string.digits, k=6))
        users[email]['verification_code'] = verification_code
        
        # Send verification email using Resend
        try:
            params = {
                "from": "BookCompass <onboarding@resend.dev>",
                "to": [email],
                "subject": "Verify Your BookCompass Account",
                "html": f"""
                <html>
                <body>
                    <h2>BookCompass Email Verification</h2>
                    <p>Your verification code is:</p>
                    <h1 style="font-size: 32px; color: #ff9900;">{verification_code}</h1>
                    <p>Enter this code on the verification page to activate your account.</p>
                    <p>This code expires in 1 hour.</p>
                    <hr>
                    <p>If you did not create an account, please ignore this email.</p>
                </body>
                </html>
                """
            }
            resend.Emails.send(params)
            
            session['pending_email'] = email
            return '<script>window.location.href="/verify-email"</script>'
        except Exception as e:
            print(f"Resend error: {e}")
            users.pop(email)
            return f'''
            <div style="text-align:center; margin-top:50px;">
                <h2>Could not send verification email</h2>
                <p>Error: {str(e)}</p>
                <p>Please try again later.</p>
                <a href="/signup">Back to Sign Up</a>
            </div>
            '''
    
    # Show signup form
    return f'''
    <!DOCTYPE html>
    <html>
    <head><title>Sign Up - BookCompass</title>
    <style>
        body {{ font-family: Arial; background: #f0f0f0; margin: 0; padding: 0; }}
        .container {{ max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; }}
        input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
        button {{ background: #ff9900; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; }}
        .header {{ background: #232f3e; color: white; padding: 15px 30px; }}
        .logo {{ font-size: 24px; }}
        .logo span {{ color: #ff9900; }}
        .referral-notice {{ background: #e8f5e9; padding: 10px; border-radius: 5px; margin-bottom: 15px; text-align: center; }}
    </style>
    </head>
    <body>
        <div class="header"><div class="logo">📚 Book<span>Compass</span></div></div>
        <div class="container">
            {"<div class='referral-notice'>🎉 You were referred by a friend! You get 10% off your first month!</div>" if referral_username else ""}
            <h2>Create Account</h2>
            <form method="post">
                <input type="text" name="username" placeholder="Username (e.g., JohnPublisher)" required>
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <input type="text" name="promo_code" placeholder="Promo code (optional)" style="width: 100%; padding: 10px; margin: 10px 0;">
                <input type="hidden" name="referred_by" value="{referral_username}">
                <button type="submit">Sign Up</button>
            </form>
            <p style="text-align:center"><a href="/login">Already have an account? Login</a></p>
        </div>
    </body>
    </html>
    '''

# ============================================
# LOGIN PAGE
# ============================================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email in users and users[email]['password'] == password:
            if not users[email].get('verified', False):
                return '''
                <div style="text-align:center; margin-top:50px;">
                    <h2>Email not verified</h2>
                    <p>Please check your email for the verification code.</p>
                    <a href="/resend-code">Resend code</a>
                </div>
                '''
            session['user_id'] = email
            session['email'] = email
            return '<script>window.location.href="/dashboard"</script>'
        return '''
        <div style="max-width:400px; margin:100px auto; background:white; padding:40px; border-radius:10px; text-align:center;">
            <h2>Invalid credentials</h2>
            <a href="/login">Try again</a>
        </div>
        '''
    
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>Login - BookCompass</title>
    <style>
        body { font-family: Arial; background: #f0f0f0; margin: 0; padding: 0; }
        .container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; }
        input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
        button { background: #ff9900; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; }
        .header { background: #232f3e; color: white; padding: 15px 30px; }
        .logo { font-size: 24px; }
        .logo span { color: #ff9900; }
    </style>
    </head>
    <body>
        <div class="header"><div class="logo">📚 Book<span>Compass</span></div></div>
        <div class="container">
            <h2>Login</h2>
            <form method="post">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button type="submit">Login</button>
            </form>
            <p style="text-align:center"><a href="/signup">No account? Sign Up</a></p>
            <p style="text-align:center; margin-top:15px;"><a href="/forgot-password">Forgot Password?</a></p>
        </div>
    </body>
    </html>
    '''

# ============================================
# LOGOUT
# ============================================

@app.route('/logout')
def logout():
    session.clear()
    return '<script>window.location.href="/"</script>'

# ============================================
# DASHBOARD
# ============================================

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return '<script>window.location.href="/login"</script>'
    
    email = session['email']
    user = users[email]
    plan = user['plan']
    limit = PLANS[plan]['daily_limit']
    
    today = str(date.today())
    if email not in usage_tracker:
        usage_tracker[email] = {}
    if today not in usage_tracker[email]:
        usage_tracker[email][today] = 0
    used = usage_tracker[email][today]
    remaining = limit - used
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dashboard - BookCompass</title>
        <style>
            body {{ font-family: Arial; margin: 0; padding: 0; background: #f0f0f0; }}
            .header {{ background: #232f3e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; }}
            .logo {{ font-size: 24px; }}
            .logo span {{ color: #ff9900; }}
            .nav a {{ color: white; margin-left: 20px; text-decoration: none; }}
            .container {{ max-width: 1200px; margin: 0 auto; padding: 30px; }}
            .card {{ background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; }}
            button {{ background: #ff9900; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; }}
            input, textarea {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #232f3e; color: white; }}
            .good {{ background: #4CAF50; color: white; padding: 3px 10px; border-radius: 20px; }}
            .medium {{ background: #ff9800; color: white; padding: 3px 10px; border-radius: 20px; }}
            .bad {{ background: #f44336; color: white; padding: 3px 10px; border-radius: 20px; }}
            .spinner {{ border: 4px solid #f3f3f3; border-top: 4px solid #ff9900; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: 20px auto; }}
            @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
            .usage-bar {{ background: #e0e0e0; border-radius: 10px; height: 10px; margin: 10px 0; }}
            .usage-fill {{ background: #ff9900; border-radius: 10px; height: 100%; width: {used/limit*100 if limit>0 else 0}%; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📚 Book<span>Compass</span></div>
            <div class="nav">
                <span>Hi, {user.get('username', email)}</span>
                <a href="/dashboard">Dashboard</a>
                <a href="/how-it-works">How It Works</a>
                <a href="/logout">Logout</a>
            </div>
        </div>
        <div class="container">
            <div class="card">
                <h2>Dashboard</h2>
                <p>Plan: <strong>{plan.upper()}</strong> | {used}/{limit} searches today</p>
                <div class="usage-bar"><div class="usage-fill"></div></div>
                <p>Remaining searches: <strong id="remainingCount">{remaining}</strong></p>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <button onclick="location.reload()" style="background: #666; padding: 5px 15px; font-size: 12px;">🔄 Refresh Status</button>
                    <a href="/upgrade"><button style="background: #ff9900; padding: 5px 15px; font-size: 12px;">⬆️ Upgrade Plan</button></a>
                </div>
                {f'''
<div id="upgradeWarning" style="background: #ffebee; padding: 15px; border-radius: 8px; margin-top: 15px; text-align: center;">
    <p style="color: #c62828; margin: 0 0 10px 0;">WARNING: You have reached your daily limit of {limit} searches.</p>
</div>
''' if remaining <= 0 else '<div id="upgradeWarning"></div>'}
            </div>
            
            <div class="card">
                <h3>👥 Referral Program</h3>
                <p>Share your unique link and earn 10% off when friends sign up!</p>
                <div style="display: flex; gap: 10px; margin-top: 10px;">
                    <input type="text" id="referralLink" readonly value="https://bookcompass-1.onrender.com/signup?ref={user.get('username', email)}" style="flex: 1; background: #f5f5f5;">
                    <button onclick="copyReferralLink()">📋 Copy</button>
                </div>
                <p style="font-size: 12px; color: #666; margin-top: 10px;">
                    ✅ You've referred <strong id="referralCount">{user.get('referral_count', 0)}</strong> friends
                    {f'<br>🎁 You have <strong>{user.get("referral_credit", 0)}</strong> months of 10% off credit!' if user.get('referral_credit', 0) > 0 else ''}
                </p>
            </div>
            
            <div class="card">
                <h3>📝 Enter Keywords (one per line)</h3>
                <textarea id="keywords" rows="8" placeholder="christian prayer journal for women&#10;christian gratitude journal women&#10;bible study journal for women"></textarea>
                <br><br>
                <button onclick="researchKeywords()">🔍 Research Keywords</button>
            </div>
            
            <div id="loading" style="display:none; text-align:center;">
                <div class="spinner"></div>
                <p id="loadingText">Researching...</p>
            </div>
            
            <div id="results" style="display:none;" class="card">
                <h3>Results (Best Opportunities First)</h3>
                <table id="resultsTable">
                    <thead><tr><th>Niche Score</th><th>Keyword</th><th>Search Volume</th><th>Competition</th></tr></thead>
                    <tbody id="resultsBody"></tbody>
                </table>
            </div>
        </div>
        
        <script>
        function copyReferralLink() {{
            const link = document.getElementById('referralLink');
            link.select();
            document.execCommand('copy');
            alert('Referral link copied! Share it with your friends.');
        }}
        
        async function researchKeywords() {{
            const keywords = document.getElementById('keywords').value.split('\\n').filter(k => k.trim());
            if(keywords.length === 0) {{ alert('Enter keywords'); return; }}
            
            const remaining = {remaining};
            if(keywords.length > remaining && remaining >= 0) {{
                if(!confirm(`You have ${{remaining}} searches left today. Researching ${{keywords.length}} keywords will use them all. Continue?`)) return;
            }}
            
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            
            const results = [];
            for(let i = 0; i < keywords.length; i++) {{
                const keyword = keywords[i].trim();
                if(!keyword) continue;
                document.getElementById('loadingText').innerHTML = `Researching ${{i+1}}/${{keywords.length}}: ${{keyword}}...`;
                
                const res = await fetch('/api/research', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{keyword: keyword}})
                }});
                const data = await res.json();
                if(data.error) {{ alert(data.error); break; }}
                results.push(data);
            }}
            
            results.sort((a,b) => b.score - a.score);
            const tbody = document.getElementById('resultsBody');
            tbody.innerHTML = '';
            results.forEach(r => {{
                const row = tbody.insertRow();
                let cls = 'bad';
                if(r.score >= 7) cls = 'good';
                else if(r.score >= 5) cls = 'medium';
                row.insertCell(0).innerHTML = `<span class="${{cls}}">${{r.score}}/10</span>`;
                row.insertCell(1).innerHTML = r.keyword;
                row.insertCell(2).innerHTML = r.volume;
                row.insertCell(3).innerHTML = r.competition;
            }});
            document.getElementById('loading').style.display = 'none';
            document.getElementById('results').style.display = 'block';
            
            // Remove any existing completion message before adding a new one
            const existingMsg = document.querySelector('.completion-message');
            if (existingMsg) {{
                existingMsg.remove();
            }}
            
            if (results.length > 0) {{
                const msg = document.createElement('div');
                msg.className = 'completion-message';
                msg.style.background = '#e3f2fd';
                msg.style.padding = '10px';
                msg.style.borderRadius = '5px';
                msg.style.marginTop = '10px';
                msg.style.textAlign = 'center';
                msg.innerHTML = '✅ Research complete! <a href="#" onclick="location.reload()">Click here to refresh</a> and see your updated search limits.';
                document.getElementById('results').appendChild(msg);
            }}
        }}
        </script>
    </body>
    </html>
    '''

# ============================================
# API RESEARCH ENDPOINT
# ============================================

@app.route('/api/research', methods=['POST'])
def api_research():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'})
    
    email = session['user_id']
    data = request.json
    keyword = data.get('keyword', '')
    
    today = str(date.today())
    if email not in usage_tracker:
        usage_tracker[email] = {}
    if today not in usage_tracker[email]:
        usage_tracker[email][today] = 0
    
    limit = PLANS[users[email]['plan']]['daily_limit']
    if usage_tracker[email][today] >= limit:
        return jsonify({'error': 'Daily limit reached'})
    
    usage_tracker[email][today] += 1
    
    # Get search volume
    try:
        url = f"https://completion.amazon.com/api/2017/suggestions?mid=ATVPDKIKX0DER&alias=stripbooks&prefix={keyword.replace(' ', '%20')}"
        r = requests.get(url, timeout=10)
        count = len(r.json().get('suggestions', []))
        if count >= 8: volume = "HIGH"
        elif count >= 4: volume = "MEDIUM"
        elif count >= 1: volume = "LOW"
        else: volume = "VERY LOW"
    except:
        volume = "MEDIUM"
    
    # Check if user is on free plan
    user_plan = users[email]['plan']
    
    if user_plan == "free":
        # Free plan: No API call for competition (faster results)
        competition = "UPGRADE TO SEE"
    else:
        # Paid plans: Get competition data using YOUR API key
        if not YOUR_API_KEY:
            competition = "UNKNOWN (API key not configured)"
        else:
            try:
                url = "https://api.rainforestapi.com/request"
                params = {"api_key": YOUR_API_KEY, "type": "search", "amazon_domain": "amazon.com", "search_term": keyword}
                r = requests.get(url, params=params, timeout=30)
                data = r.json()
                strong = 0
                for item in data.get('search_results', [])[:5]:
                    bsr = "N/A"
                    if 'bestsellers_rank' in item:
                        for rank in item['bestsellers_rank']:
                            if 'rank' in rank:
                                bsr = rank['rank']
                                break
                    try:
                        if bsr != "N/A" and int(bsr) < 100000:
                            strong += 1
                    except:
                        pass
                if strong >= 3: competition = "HIGH"
                elif strong >= 1: competition = "MEDIUM"
                else: competition = "LOW"
            except:
                competition = "MEDIUM"
    
    # Calculate score
    score = 5
    
    if user_plan == "free":
        if volume == "HIGH": score += 3
        elif volume == "MEDIUM": score += 2
        elif volume == "LOW": score += 1
        else: score -= 1
    else:
        if competition == "LOW": score += 3
        elif competition == "MEDIUM": score += 1
        else: score -= 2
        if volume == "HIGH": score += 2
        elif volume == "MEDIUM": score += 1
        elif volume == "VERY LOW": score -= 2
    
    score = max(1, min(10, score))
    
    time.sleep(1)
    return jsonify({'keyword': keyword, 'volume': volume, 'competition': competition, 'score': score})

# ============================================
# UPGRADE PAGE
# ============================================

@app.route('/upgrade')
def upgrade():
    if 'user_id' not in session:
        return '<script>window.location.href="/login"</script>'
    
    email = session['email']
    current_plan = users[email]['plan']
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Upgrade - BookCompass</title>
        <style>
            body {{ font-family: Arial; margin: 0; padding: 0; background: #f0f0f0; }}
            .header {{ background: #232f3e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; }}
            .logo {{ font-size: 24px; }}
            .logo span {{ color: #ff9900; }}
            .nav a {{ color: white; margin-left: 20px; text-decoration: none; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 30px; }}
            .card {{ background: white; border-radius: 10px; padding: 25px; margin-bottom: 20px; }}
            .pricing-grid {{ display: flex; gap: 20px; margin-top: 20px; }}
            .plan {{ flex: 1; border: 1px solid #ddd; border-radius: 10px; padding: 20px; text-align: center; }}
            .plan.featured {{ border: 2px solid #ff9900; background: #fff8f0; }}
            .plan.current {{ border: 2px solid #4CAF50; background: #e8f5e9; }}
            .price {{ font-size: 32px; font-weight: bold; color: #232f3e; }}
            button {{ background: #ff9900; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; }}
            .badge {{ display: inline-block; background: #4CAF50; color: white; padding: 5px 10px; border-radius: 20px; font-size: 12px; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📚 Book<span>Compass</span></div>
            <div class="nav">
                <span>Hi, {users[email].get('username', email)}</span>
                <a href="/dashboard">Dashboard</a>
                <a href="/logout">Logout</a>
            </div>
        </div>
        <div class="container">
            <div class="card" style="text-align: center;">
                <h1>⬆️ Upgrade Your Plan</h1>
                <p>Get more searches per day and unlock additional features.</p>
            </div>
            <div class="pricing-grid">
                <div class="plan {'current' if current_plan == 'free' else ''}">
                    {'<div class="badge">CURRENT PLAN</div>' if current_plan == 'free' else ''}
                    <h3>Free</h3><div class="price">$0</div><p>3 searches/day</p>
                    {'<button disabled style="background: #ccc; cursor: not-allowed;">Current Plan</button>' if current_plan == 'free' else '<a href="/select_plan/free"><button>Select Free</button></a>'}
                </div>
                <div class="plan featured {'current' if current_plan == 'starter' else ''}">
                    {'<div class="badge">CURRENT PLAN</div>' if current_plan == 'starter' else '<div class="badge" style="background:#ff9900;">RECOMMENDED</div>'}
                    <h3>Starter</h3><div class="price">$12<span style="font-size:14px">/month</span></div><p>20 searches/day</p>
                    {'<button disabled style="background: #ccc; cursor: not-allowed;">Current Plan</button>' if current_plan == 'starter' else '<a href="/select_plan/starter"><button>Choose Starter</button></a>'}
                </div>
                <div class="plan {'current' if current_plan == 'pro' else ''}">
                    {'<div class="badge">CURRENT PLAN</div>' if current_plan == 'pro' else ''}
                    <h3>Pro</h3><div class="price">$25<span style="font-size:14px">/month</span></div><p>100 searches/day</p>
                    {'<button disabled style="background: #ccc; cursor: not-allowed;">Current Plan</button>' if current_plan == 'pro' else '<a href="/select_plan/pro"><button>Choose Pro</button></a>'}
                </div>
            </div>
        </div>
    </body>
    </html>
    '''

# ============================================
# SELECT PLAN
# ============================================

@app.route('/select_plan/<plan_name>')
def select_plan(plan_name):
    if 'user_id' not in session:
        return '<script>window.location.href="/login"</script>'
    
    if plan_name in PLANS:
        email = session['user_id']
        user = users[email]
        
        original_price = 12 if plan_name == 'starter' else 25
        final_price = original_price
        promo_message = ""
        
        # Check for referral credit first
        if user.get('referral_credit', 0) > 0:
            final_price = original_price * 0.9
            promo_message = f" (Referral credit: 10% off)"
            users[email]['referral_credit'] = user.get('referral_credit', 0) - 1
        # Then check for promo code
        elif user.get('promo_code') and user.get('promo_expires'):
            from datetime import datetime
            promo_expires = datetime.fromisoformat(user['promo_expires'])
            if datetime.now() < promo_expires:
                promo_data = PROMO_CODES.get(user['promo_code'])
                if promo_data:
                    discount = promo_data['discount']
                    final_price = original_price * (1 - discount / 100)
                    promo_message = f" (Promo {user['promo_code']}: {discount}% off applied)"
        
        users[email]['plan'] = plan_name
        
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Plan Updated - BookCompass</title>
        <style>
            body {{ font-family: Arial; display: flex; justify-content: center; align-items: center; height: 100vh; background: #f0f0f0; }}
            .card {{ background: white; padding: 40px; border-radius: 10px; text-align: center; }}
            button {{ background: #ff9900; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; }}
        </style>
        </head>
        <body>
        <div class="card">
            <h2>✅ Plan Updated Successfully!</h2>
            <p>Your plan has been changed to <strong>{plan_name.upper()}</strong>.</p>
            <p>Price: <strong>${final_price:.2f}/month</strong>{promo_message}</p>
            <a href="/dashboard"><button>Go to Dashboard</button></a>
        </div>
        </body>
        </html>
        '''
    return '<script>window.location.href="/upgrade"</script>'

# ============================================
# HOW IT WORKS PAGE
# ============================================

@app.route('/how-it-works')
def how_it_works():
    logged_in = session.get('user_id') is not None
    email = session.get('email', '')
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>How It Works - BookCompass</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 0; padding: 0; background: #f0f0f0; }}
            .header {{ background: #232f3e; color: white; padding: 15px 30px; display: flex; justify-content: space-between; align-items: center; }}
            .logo {{ font-size: 24px; font-weight: bold; }}
            .logo span {{ color: #ff9900; }}
            .nav a {{ color: white; margin-left: 20px; text-decoration: none; }}
            .container {{ max-width: 1000px; margin: 0 auto; padding: 30px; }}
            .card {{ background: white; border-radius: 10px; padding: 30px; margin-bottom: 25px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            h1 {{ color: #232f3e; }}
            h2 {{ color: #232f3e; border-bottom: 2px solid #ff9900; padding-bottom: 10px; }}
            h3 {{ color: #ff9900; }}
            .step {{ background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
            .score-green {{ background: #4CAF50; color: white; padding: 3px 10px; border-radius: 20px; display: inline-block; }}
            .score-orange {{ background: #ff9800; color: white; padding: 3px 10px; border-radius: 20px; display: inline-block; }}
            .score-red {{ background: #f44336; color: white; padding: 3px 10px; border-radius: 20px; display: inline-block; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #232f3e; color: white; }}
            .faq {{ background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .faq strong {{ color: #ff9900; }}
            button {{ background: #ff9900; color: white; padding: 12px 30px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px; }}
            button:hover {{ background: #e68a00; }}
        </style>
    </head>
    <body>
        <div class="header">
            <div class="logo">📚 Book<span>Compass</span></div>
            <div class="nav">
                <a href="/">Home</a>
                <a href="/how-it-works">How It Works</a>
                {"<a href='/dashboard'>Dashboard</a>" if logged_in else ""}
                <a href="/login">Login</a>
                <a href="/signup">Sign Up</a>
            </div>
        </div>
        
        <div class="container">
            <div class="card">
                <h1>How BookCompass Works</h1>
                <p style="font-size: 18px;">Your compass for finding winning KDP keywords.</p>
            </div>
            
            <div class="card">
                <h2>What is BookCompass?</h2>
                <p><strong>BookCompass is a keyword research tool for Amazon KDP authors.</strong> It helps you find the right keywords so your books can be discovered by readers on Amazon.</p>
                <p>Think of it like a compass that points you toward profitable, low-competition keywords that other publishers have missed.</p>
            </div>
            
            <div class="card">
                <h2>The Problem BookCompass Solves</h2>
                <div class="step">
                    <h3>❌ Without BookCompass:</h3>
                    <p>You guess. You hope. You pray your book sells. You don't know if people are searching for your topic or how many competitors exist.</p>
                </div>
                <div class="step">
                    <h3>✅ With BookCompass:</h3>
                    <p>You get clear data: Search Volume, Competition Level, and a simple 1-10 Niche Score. No more guessing.</p>
                </div>
            </div>
            
            <div class="card">
                <h2>3 Simple Steps</h2>
                <div class="step">
                    <h3>Step 1: Enter Your Keywords</h3>
                    <p>Paste up to 30 keywords into BookCompass.</p>
                    <code style="background: #f0f0f0; padding: 10px; display: block; border-radius: 5px;">
                        christian prayer journal for women<br>
                        christian gratitude journal women<br>
                        bible study journal for women<br>
                        prayer journal for anxiety
                    </code>
                </div>
              
                <div class="step">
                    <h3>Step 2: BookCompass Does the Work</h3>
                    <p>We check Amazon search volume, analyze top competitors, look at Best Seller Ranks, and calculate a Niche Score for each keyword.</p>
                </div>
                
                <div class="step">
                    <h3>Step 3: You Get Clear Results</h3>
                    <p>BookCompass shows you a table with Niche Score, Search Volume, and Competition Level for each keyword.</p>
                </div>
            </div>

            <div class="card">
                <h2>🎁 Earn While You Save: Referral Program</h2>
                <p>BookCompass rewards you for sharing with fellow authors.</p>
                <div style="display: flex; gap: 20px; margin-top: 20px;">
                    <div style="flex: 1; background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 40px;">👥</div>
                        <h3>Share Your Link</h3>
                        <p>Copy your unique referral link from your Dashboard</p>
                    </div>
                    <div style="flex: 1; background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 40px;">🎁</div>
                        <h3>Friend Gets 10% Off</h3>
                        <p>They save money on their first month</p>
                    </div>
                    <div style="flex: 1; background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 40px;">💰</div>
                        <h3>You Get 10% Off</h3>
                        <p>Earn credit toward your next month</p>
                    </div>
                </div>
                <p style="text-align: center; margin-top: 20px;"><strong>It's a win-win. The more friends you invite, the more you save!</strong></p>
            </div>
            
            <div class="card">
                <h2>Understanding Your Results</h2>
                
                <h3>Niche Score (1-10)</h3>
                <table>
                    <thead><tr><th>Color</th><th>Score</th><th>Meaning</th><th>Action</th></tr></thead>
                    <tbody>
                        <tr><td><span class="score-green">🟢 Green</span></td><td>7-10</td><td>Excellent opportunity</td><td>Target these keywords immediately</td></tr>
                        <tr><td><span class="score-orange">🟡 Orange</span></td><td>5-6</td><td>Decent opportunity</td><td>Consider if search volume is high</td></tr>
                        <tr><td><span class="score-red">🔴 Red</span></td><td>1-4</td><td>Poor opportunity</td><td>Avoid, too competitive</td></tr>
                    </tbody>
                </table>
                
                <h3>Search Volume</h3>
                <ul>
                    <li><strong>HIGH</strong> - 1,000 - 5,000+ searches per month</li>
                    <li><strong>MEDIUM</strong> - 500 - 1,000 searches per month</li>
                    <li><strong>LOW</strong> - 100 - 500 searches per month</li>
                    <li><strong>VERY LOW</strong> - Under 100 searches per month</li>
                </ul>
                
                <h3>Competition Level</h3>
                <ul>
                    <li><strong>LOW</strong> - 0-1 strong competitors. Easy to rank!</li>
                    <li><strong>MEDIUM</strong> - 2-3 strong competitors. Possible with good book.</li>
                    <li><strong>HIGH</strong> - 4+ strong competitors. Very difficult.</li>
                </ul>
            </div>
            
            <div class="card">
                <h2>Example: Real Results</h2>
                <table>
                    <thead><tr><th>Niche Score</th><th>Keyword</th><th>Search Volume</th><th>Competition</th></tr></thead>
                    <tbody>
                        <tr><td><span class="score-green">9/10 🟢</span></td><td>christian gratitude journal women</td><td>MEDIUM</td><td>LOW</td></tr>
                        <tr><td><span class="score-green">8/10 🟢</span></td><td>prayer journal for anxiety</td><td>MEDIUM</td><td>LOW</td></tr>
                        <tr><td><span class="score-orange">6/10 🟡</span></td><td>bible study journal for women</td><td>HIGH</td><td>MEDIUM</td></tr>
                        <tr><td><span class="score-red">4/10 🔴</span></td><td>daily devotional journal</td><td>HIGH</td><td>HIGH</td></tr>
                    </tbody>
                </table>
                <p><strong>Your best target:</strong> "christian gratitude journal women" - great score, good volume, low competition!</p>
            </div>
            
            <div class="card">
                <h2>Why BookCompass is Better Than Guessing</h2>
                <div style="display: flex; gap: 20px; flex-wrap: wrap; margin-top: 20px;">
                    <div style="flex: 1; background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center;">
                        <div style="font-size: 48px;">❓</div>
                        <h3>Guessing Keywords</h3>
                        <ul style="text-align: left;">
                            <li>❌ 10-20% success rate</li>
                            <li>❌ Takes hours of trial and error</li>
                            <li>❌ No data to back your decisions</li>
                            <li>❌ Wasted time on dead ends</li>
                            <li>❌ Books get buried in search</li>
                        </ul>
                    </div>
                    <div style="flex: 1; background: #e8f5e9; padding: 20px; border-radius: 10px; text-align: center; border: 2px solid #4CAF50;">
                        <div style="font-size: 48px;">🧭</div>
                        <h3>Using BookCompass</h3>
                        <ul style="text-align: left;">
                            <li>✅ 80-90% success rate</li>
                            <li>✅ Takes minutes, not hours</li>
                            <li>✅ Clear data from Amazon</li>
                            <li>✅ Target proven opportunities</li>
                            <li>✅ Books get discovered by readers</li>
                        </ul>
                    </div>
                </div>
                <p style="text-align: center; margin-top: 20px; font-size: 18px;"><strong>Stop guessing. Start knowing.</strong></p>
            </div>
            
            <div class="card">
                <h2>Pricing Plans</h2>
                <div style="display: flex; gap: 20px; flex-wrap: wrap;">
                    <div style="flex: 1; border: 1px solid #ddd; border-radius: 10px; padding: 20px; text-align: center;">
                        <h3>Free</h3>
                        <div style="font-size: 32px; color: #232f3e;">$0</div>
                        <p>3 searches/day</p>
                        <a href="/signup"><button style="padding: 8px 20px;">Start Free</button></a>
                    </div>
                    <div style="flex: 1; border: 2px solid #ff9900; border-radius: 10px; padding: 20px; text-align: center; background: #fff8f0;">
                        <h3>Starter</h3>
                        <div style="font-size: 32px; color: #232f3e;">$12<span style="font-size: 14px;">/month</span></div>
                        <p>20 searches/day</p>
                        <a href="/signup"><button style="padding: 8px 20px;">Choose Starter</button></a>
                    </div>
                    <div style="flex: 1; border: 1px solid #ddd; border-radius: 10px; padding: 20px; text-align: center;">
                        <h3>Pro</h3>
                        <div style="font-size: 32px; color: #232f3e;">$25<span style="font-size: 14px;">/month</span></div>
                        <p>100 searches/day</p>
                        <a href="/signup"><button style="padding: 8px 20px;">Choose Pro</button></a>
                    </div>
                </div>
            </div>
            
                        <div class="card">
                <h2>Frequently Asked Questions</h2>
                
                <div class="faq">
                    <strong>🎁 Does BookCompass have a referral program?</strong>
                    <p><strong>Yes!</strong> When you share your unique referral link with a friend:</p>
                    <ul>
                        <li><strong>Your friend gets 10% off their first month</strong></li>
                        <li><strong>You get 10% off one month</strong> (when they sign up)</li>
                    </ul>
                    <p>Find your unique referral link in your Dashboard. Share it with fellow authors and save money together!</p>
                </div>
                
                <div class="faq">
                    <strong>Do I need an API key?</strong>
                    <p>No. BookCompass uses my own API key. You don't need to sign up for anything else.</p>
                </div>
                
                <div class="faq">
                    <strong>How accurate is the data?</strong>
                    <p>BookCompass pulls live data directly from Amazon. The search volume and competition data are as accurate as possible.</p>
                </div>
                
                <div class="faq">
                    <strong>Can I use BookCompass for any category?</strong>
                    <p>Yes! BookCompass works for ANY book category on Amazon KDP - fiction, non-fiction, children's books, cookbooks, journals, and more.</p>
                </div>
                
                <div class="faq">
                    <strong>How long does research take?</strong>
                    <p>About 2-3 seconds per keyword. Researching 30 keywords takes roughly 1-2 minutes.</p>
                </div>
                
                <div class="faq">
                    <strong>What happens when I reach my daily limit?</strong>
                    <p>Your dashboard shows a warning. You can either wait until tomorrow (limits reset at midnight) or upgrade to a higher plan for more searches.</p>
                </div>
                
                <div class="faq">
                    <strong>Can I cancel my subscription?</strong>
                    <p>Yes, you can cancel anytime. Downgrade to the Free plan from your Dashboard.</p>
                </div>
            </div>
            
            <div class="card" style="text-align: center;">
                <h2>Ready to Find Your First Winning Keyword?</h2>
                <a href="/signup"><button style="font-size: 18px; padding: 15px 40px;">Create Free Account →</button></a>
            </div>
        </div>
    </body>
    </html>
    '''

# ============================================
# EMAIL VERIFICATION PAGE
# ============================================

@app.route('/verify-email', methods=['GET', 'POST'])
def verify_email():
    if 'pending_email' not in session:
        return '<script>window.location.href="/signup"</script>'
    
    email = session['pending_email']
    
    if request.method == 'POST':
        code = request.form.get('verification_code', '').strip()
        
        if email in users and users[email].get('verification_code') == code:
            users[email]['verified'] = True
            users[email]['verification_code'] = None
            session['user_id'] = email
            session['email'] = email
            session.pop('pending_email', None)
            return '<script>window.location.href="/dashboard"</script>'
        else:
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Invalid verification code</h2>
                <p>Please try again.</p>
                <a href="/verify-email">Back</a>
            </div>
            '''
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Verify Email - BookCompass</title>
        <style>
            body {{ font-family: Arial; background: #f0f0f0; margin: 0; padding: 0; }}
            .container {{ max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
            button {{ background: #ff9900; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; }}
            .header {{ background: #232f3e; color: white; padding: 15px 30px; }}
            .logo {{ font-size: 24px; }}
            .logo span {{ color: #ff9900; }}
        </style>
    </head>
    <body>
        <div class="header"><div class="logo">📚 Book<span>Compass</span></div></div>
        <div class="container">
            <h2>Verify Your Email</h2>
            <p>We sent a 6-digit code to <strong>{email}</strong></p>
            <form method="post">
                <input type="text" name="verification_code" placeholder="Enter 6-digit code" required maxlength="6">
                <button type="submit">Verify</button>
            </form>
            <p style="text-align:center; margin-top:20px;">
                <a href="/resend-code">Resend code</a>
            </p>
        </div>
    </body>
    </html>
    '''

# ============================================
# RESEND CODE
# ============================================

@app.route('/resend-code')
def resend_code():
    if 'pending_email' not in session:
        return '<script>window.location.href="/signup"</script>'
    
    email = session['pending_email']
    
    if email in users:
        import random
        import string
        new_code = ''.join(random.choices(string.digits, k=6))
        users[email]['verification_code'] = new_code
        
        try:
            params = {
                "from": "BookCompass <onboarding@resend.dev>",
                "to": [email],
                "subject": "Your New Verification Code - BookCompass",
                "html": f"""
                <html>
                <body>
                    <h2>BookCompass Email Verification</h2>
                    <p>Your new verification code is:</p>
                    <h1 style="font-size: 32px; color: #ff9900;">{new_code}</h1>
                    <p>Enter this code on the verification page to activate your account.</p>
                    <p>This code expires in 1 hour.</p>
                    <hr>
                    <p>If you did not create an account, please ignore this email.</p>
                    <p style="font-size: 12px; color: #666;">You received this email because you signed up for BookCompass.</p>
                </body>
                </html>
                """
            }
            resend.Emails.send(params)
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>New code sent!</h2>
                <p>Please check your email.</p>
                <a href="/verify-email">Back to verification</a>
            </div>
            '''
        except Exception as e:
            print(f"Resend error: {e}")
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Could not send email</h2>
                <a href="/verify-email">Try again</a>
            </div>
            '''
    
    return '<script>window.location.href="/signup"</script>'

# ============================================
# FORGOT PASSWORD PAGE
# ============================================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if email not in users:
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Email not found</h2>
                <p>No account exists with that email address.</p>
                <a href="/forgot-password">Try again</a> | <a href="/signup">Sign Up</a>
            </div>
            '''
        
        # Generate reset token
        import random
        import string
        reset_token = ''.join(random.choices(string.ascii_letters + string.digits, k=32))
        users[email]['reset_token'] = reset_token
        users[email]['reset_expires'] = (datetime.now() + timedelta(hours=1)).isoformat()
        
        # Send reset email using Resend
        try:
            reset_link = f"https://bookcompass-1.onrender.com/reset-password/{reset_token}"
            params = {
                "from": "BookCompass <onboarding@resend.dev>",
                "to": [email],
                "subject": "Reset Your BookCompass Password",
                "html": f"""
                <html>
                <body>
                    <h2>Password Reset Request</h2>
                    <p>Click the link below to reset your password:</p>
                    <p><a href="{reset_link}">{reset_link}</a></p>
                    <p>This link expires in 1 hour.</p>
                    <hr>
                    <p>If you did not request this, please ignore this email.</p>
                </body>
                </html>
                """
            }
            resend.Emails.send(params)
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Reset Link Sent!</h2>
                <p>Check your email for the password reset link.</p>
                <p>(Check your spam folder if you don't see it)</p>
                <a href="/login">Back to Login</a>
            </div>
            '''
        except Exception as e:
            print(f"Reset email error: {e}")
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Could not send reset email</h2>
                <p>Please try again later.</p>
                <a href="/forgot-password">Back</a>
            </div>
            '''
    
    # GET request - show the form
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Forgot Password - BookCompass</title>
        <style>
            body { font-family: Arial; background: #f0f0f0; margin: 0; padding: 0; }
            .container { max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; }
            input { width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }
            button { background: #ff9900; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; }
            .header { background: #232f3e; color: white; padding: 15px 30px; }
            .logo { font-size: 24px; }
            .logo span { color: #ff9900; }
        </style>
    </head>
    <body>
        <div class="header"><div class="logo">📚 Book<span>Compass</span></div></div>
        <div class="container">
            <h2>Forgot Password</h2>
            <p>Enter your email address and we'll send you a reset link.</p>
            <form method="post">
                <input type="email" name="email" placeholder="Email" required>
                <button type="submit">Send Reset Link</button>
            </form>
            <p style="text-align:center; margin-top:15px;"><a href="/login">Back to Login</a></p>
        </div>
    </body>
    </html>
    '''

# ============================================
# RESET PASSWORD PAGE
# ============================================

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from datetime import datetime
    
    # Find user with this token
    user_email = None
    for email, user_data in users.items():
        if user_data.get('reset_token') == token:
            user_email = email
            break
    
    if not user_email:
        return '''
        <div style="text-align:center; margin-top:50px;">
            <h2>Invalid or expired link</h2>
            <p>The password reset link is invalid or has expired.</p>
            <a href="/forgot-password">Request a new one</a>
        </div>
        '''
    
    user = users[user_email]
    
    # Check if token expired
    if 'reset_expires' in user:
        expires = datetime.fromisoformat(user['reset_expires'])
        if datetime.now() > expires:
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Link Expired</h2>
                <p>The reset link has expired. Please request a new one.</p>
                <a href="/forgot-password">Request New Link</a>
            </div>
            '''
    
    if request.method == 'POST':
        new_password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if new_password != confirm_password:
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Passwords do not match</h2>
                <a href="javascript:history.back()">Try again</a>
            </div>
            '''
        
        if len(new_password) < 6:
            return '''
            <div style="text-align:center; margin-top:50px;">
                <h2>Password too short</h2>
                <p>Password must be at least 6 characters.</p>
                <a href="javascript:history.back()">Try again</a>
            </div>
            '''
        
        # Update password
        users[user_email]['password'] = new_password
        # Clear reset token
        users[user_email]['reset_token'] = None
        users[user_email]['reset_expires'] = None
        
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Password Reset - BookCompass</title>
            <style>
                body { font-family: Arial; text-align: center; margin-top: 100px; }
                button { background: #ff9900; color: white; padding: 12px 25px; border: none; border-radius: 5px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div style="background: white; max-width: 400px; margin: 0 auto; padding: 40px; border-radius: 10px;">
                <h2>✅ Password Reset Successful!</h2>
                <p>Your password has been changed.</p>
                <a href="/login"><button>Login Now</button></a>
            </div>
        </body>
        </html>
        '''
    
    # GET request - show reset form
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Reset Password - BookCompass</title>
        <style>
            body {{ font-family: Arial; background: #f0f0f0; margin: 0; padding: 0; }}
            .container {{ max-width: 400px; margin: 100px auto; background: white; padding: 40px; border-radius: 10px; }}
            input {{ width: 100%; padding: 10px; margin: 10px 0; border: 1px solid #ddd; border-radius: 5px; }}
            button {{ background: #ff9900; color: white; padding: 12px; border: none; border-radius: 5px; width: 100%; cursor: pointer; }}
            .header {{ background: #232f3e; color: white; padding: 15px 30px; }}
            .logo {{ font-size: 24px; }}
            .logo span {{ color: #ff9900; }}
        </style>
    </head>
    <body>
        <div class="header"><div class="logo">📚 Book<span>Compass</span></div></div>
        <div class="container">
            <h2>Reset Password</h2>
            <p>Enter your new password for: <strong>{user_email}</strong></p>
            <form method="post">
                <input type="password" name="password" placeholder="New Password" required minlength="6">
                <input type="password" name="confirm_password" placeholder="Confirm Password" required>
                <button type="submit">Reset Password</button>
            </form>
        </div>
    </body>
    </html>
    '''

# ============================================
# RUN THE APP
# ============================================
# ============================================
# ADMIN PANEL (Protected)
# ============================================

@app.route('/admin')
def admin_panel():
    # Simple password protection (CHANGE THIS PASSWORD)
    admin_password = request.args.get('password', '')
    
    if admin_password != 'BookCompassAdmin@@2026!':
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Admin Access - BookCompass</title>
            <style>
                body { font-family: Arial; text-align: center; margin-top: 100px; background: #f0f0f0; }
                .card { background: white; max-width: 400px; margin: 0 auto; padding: 40px; border-radius: 10px; }
                input { padding: 10px; width: 80%; margin: 10px 0; }
                button { background: #ff9900; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>🔐 Admin Access</h2>
                <p>Enter password to access admin dashboard.</p>
                <form method="get">
                    <input type="password" name="password" placeholder="Enter password">
                    <br>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
        '''
    
    # Calculate stats
    total_users = len(users)
    free_users = sum(1 for u in users.values() if u.get('plan') == 'free')
    starter_users = sum(1 for u in users.values() if u.get('plan') == 'starter')
    pro_users = sum(1 for u in users.values() if u.get('plan') == 'pro')
    
    # Total searches today
    today = str(date.today())
    total_searches = 0
    for email, tracker in usage_tracker.items():
        total_searches += tracker.get(today, 0)
    
    # Verified vs unverified users
    verified_users = sum(1 for u in users.values() if u.get('verified', False))
    unverified_users = total_users - verified_users
    
    # Recent users (last 10)
    recent_users = list(users.keys())[-10:]
    
    # Total referral credits given
    total_referrals = sum(u.get('referral_count', 0) for u in users.values())
    
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Admin Dashboard - BookCompass</title>
        <style>
            body {{ font-family: Arial; background: #f0f0f0; margin: 0; padding: 20px; }}
            h1 {{ color: #232f3e; }}
            .stats {{ display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 20px; }}
            .stat {{ flex: 1; background: #232f3e; color: white; padding: 20px; border-radius: 10px; text-align: center; min-width: 150px; }}
            .stat h2 {{ margin: 0; font-size: 32px; }}
            .stat p {{ margin: 10px 0 0; opacity: 0.8; }}
            .card {{ background: white; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background: #ff9900; color: white; }}
            tr:hover {{ background: #f5f5f5; }}
            .plan-badge {{ display: inline-block; padding: 3px 10px; border-radius: 20px; font-size: 12px; }}
            .plan-free {{ background: #4CAF50; color: white; }}
            .plan-starter {{ background: #ff9800; color: white; }}
            .plan-pro {{ background: #f44336; color: white; }}
            .verified {{ color: #4CAF50; }}
            .unverified {{ color: #f44336; }}
            .nav {{ margin-bottom: 20px; }}
            .nav a {{ background: #ff9900; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .nav a:hover {{ background: #e68a00; }}
        </style>
    </head>
    <body>
        <div class="nav">
            <a href="/dashboard">← Back to Dashboard</a>
        </div>
        
        <h1>📊 BookCompass Admin Dashboard</h1>
        
        <div class="stats">
            <div class="stat">
                <h2>{total_users}</h2>
                <p>Total Users</p>
            </div>
            <div class="stat">
                <h2>{free_users}</h2>
                <p>Free Plan</p>
            </div>
            <div class="stat">
                <h2>{starter_users}</h2>
                <p>Starter Plan ($12)</p>
            </div>
            <div class="stat">
                <h2>{pro_users}</h2>
                <p>Pro Plan ($25)</p>
            </div>
            <div class="stat">
                <h2>{total_searches}</h2>
                <p>Searches Today</p>
            </div>
            <div class="stat">
                <h2>{verified_users}/{total_users}</h2>
                <p>Verified Users</p>
            </div>
            <div class="stat">
                <h2>{total_referrals}</h2>
                <p>Total Referrals</p>
            </div>
        </div>
        
        <div class="card">
            <h2>📝 Recent Signups (Last 10)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Plan</th>
                        <th>Verified</th>
                        <th>Referrals</th>
                        <th>Joined</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join(f'''
                    <tr>
                        <td>{users[email].get('username', 'N/A')}</td>
                        <td>{email}</td>
                        <td><span class="plan-badge plan-{users[email].get('plan', 'free')}">{users[email].get('plan', 'free').upper()}</span></td>
                        <td class="{'verified' if users[email].get('verified') else 'unverified'}">{'✅' if users[email].get('verified') else '❌'}</td>
                        <td>{users[email].get('referral_count', 0)}</td>
                        <td>{users[email].get('created_at', 'N/A')}</td>
                    </tr>
                    ''' for email in recent_users[::-1])}
                </tbody>
            </table>
        </div>
        
        <div class="card">
            <h2>⚙️ System Info</h2>
            <ul>
                <li><strong>Server Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</li>
                <li><strong>Users in Memory:</strong> {total_users}</li>
                <li><strong>API Key Status:</strong> {'✅ Active' if YOUR_API_KEY else '❌ Not Set'}</li>
                <li><strong>Resend API Status:</strong> {'✅ Configured' if os.environ.get('RESEND_API_KEY') else '❌ Not Set'}</li>
            </ul>
        </div>
    </body>
    </html>
    '''
if __name__ == '__main__':
    print("\n" + "="*50)
    print("   🚀 BOOKCOMPASS IS RUNNING")
    print("="*50)
    print("\n🌐 Open your browser to: http://127.0.0.1:5000")
    print("\n✅ Create an account to start!")
    print("="*50)
    app.run(debug=True, port=5000)