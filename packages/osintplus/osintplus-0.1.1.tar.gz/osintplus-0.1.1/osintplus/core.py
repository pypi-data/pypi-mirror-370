import socket
import subprocess
import whois
import requests
import hashlib
import re
from tqdm import tqdm
import socket

def resolve_domain(domain):
    try:
        ip = socket.gethostbyname(domain)
        return f"{domain} résolu en {ip}"
    except socket.gaierror:
        return f"Impossible de résoudre {domain}"

def ping_host(host):
    try:
        output = subprocess.check_output(["ping", "-c", "4", host], stderr=subprocess.STDOUT, text=True)
        return output
    except subprocess.CalledProcessError as e:
        return f"Erreur lors du ping :\n{e.output}"

def get_whois_info(domain):
    try:
        w = whois.whois(domain)
        return w.text
    except Exception as e:
        return f"Erreur WHOIS : {e}"

def get_headers(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url
        response = requests.head(url, timeout=5)
        return "\n".join(f"{k}: {v}" for k, v in response.headers.items())
    except Exception as e:
        return f"Erreur lors de la récupération des headers : {e}"

def get_robots_txt(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url
        response = requests.get(f"{url}/robots.txt", timeout=5)
        return response.text if response.status_code == 200 else "robots.txt non trouvé"
    except Exception as e:
        return f"Erreur lors de la récupération de robots.txt : {e}"

# --- Nouvelles fonctionnalités ---

def get_favicon_hash(url):
    try:
        if not url.startswith("http"):
            url = "http://" + url
        favicon_url = url.rstrip("/") + "/favicon.ico"
        response = requests.get(favicon_url, timeout=5)
        if response.status_code != 200:
            return "favicon.ico non trouvé"
        md5_hash = hashlib.md5(response.content).hexdigest()
        return f"MD5 du favicon.ico : {md5_hash}"
    except Exception as e:
        return f"Erreur lors de la récupération du favicon : {e}"

def detect_technologies(url):
    """
    Simple détection de technologies via headers et body,
    avec extraction claire du serveur HTTP et de sa version.
    """
    try:
        if not url.startswith("http"):
            url = "http://" + url
        response = requests.get(url, timeout=5)
        headers = response.headers
        body = response.text.lower()

        techs = []

        # X-Powered-By
        if "x-powered-by" in headers:
            techs.append(f"X-Powered-By: {headers['x-powered-by']}")

        # CMS détectés par body
        if "wp-content" in body or "wordpress" in body:
            techs.append("WordPress détecté")
        if "joomla" in body:
            techs.append("Joomla détecté")
        if "drupal" in body:
            techs.append("Drupal détecté")
        if "shopify" in body:
            techs.append("Shopify détecté")

        # Serveur HTTP avec version extraite proprement
        if "server" in headers:
            server_header = headers["server"]
            # Exemple : "Apache/2.4.41 (Ubuntu)"
            # On peut juste afficher tel quel, ou découper en nom + version
            # Ici on découpe nom + version entre slash et espace
            import re
            match = re.match(r"([^\s/]+)(?:/([\d\.]+))?", server_header)
            if match:
                server_name = match.group(1)
                server_version = match.group(2)
                if server_version:
                    techs.append(f"Serveur HTTP: {server_name} version {server_version}")
                else:
                    techs.append(f"Serveur HTTP: {server_name}")
            else:
                techs.append(f"Serveur HTTP: {server_header}")

        if not techs:
            return "Aucune technologie détectée"
        else:
            return "\n".join(techs)
    except Exception as e:
        return f"Erreur lors de la détection technologies : {e}"


def get_links(url):
    """
    Récupère tous les liens <a href=""> sur la page.
    """
    try:
        if not url.startswith("http"):
            url = "http://" + url
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return f"Erreur HTTP {response.status_code}"
        links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
        if not links:
            return "Aucun lien trouvé"
        return "\n".join(set(links))
    except Exception as e:
        return f"Erreur lors de la récupération des liens : {e}"

def get_content_summary(url):
    """
    Récupère <title> et <h1> d’une page.
    """
    try:
        if not url.startswith("http"):
            url = "http://" + url
        response = requests.get(url, timeout=5)
        if response.status_code != 200:
            return f"Erreur HTTP {response.status_code}"
        title = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE)
        h1 = re.search(r'<h1.*?>(.*?)</h1>', response.text, re.IGNORECASE)
        summary = []
        if title:
            summary.append(f"Titre: {title.group(1).strip()}")
        if h1:
            summary.append(f"H1: {h1.group(1).strip()}")
        if not summary:
            return "Aucun titre ni H1 trouvé"
        return "\n".join(summary)
    except Exception as e:
        return f"Erreur lors de la récupération du contenu : {e}"

def port_scan(target, ports=None, show_progress=True):
    if ports is None:
        ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443,
                 445, 3306, 3389, 8080, 8443]
    elif isinstance(ports, str) and '-' in ports:
        start, end = map(int, ports.split('-'))
        ports = list(range(start, end + 1))
    elif isinstance(ports, str):
        ports = list(map(int, ports.split(',')))

    try:
        ip = socket.gethostbyname(target)
        open_ports = []

        iterator = tqdm(ports, desc="🔍 Scan des ports", unit="port") if show_progress else ports
        for port in iterator:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((ip, port))
            sock.close()

            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except:
                    service = "Inconnu"
                open_ports.append((port, service))

        if open_ports:
            result_str = f"Ports ouverts sur {target} ({ip}) :\n"
            for port, service in open_ports:
                result_str += f"- {port:<5} ({service.upper()})\n"
            return result_str.strip()
        else:
            return f"Aucun port ouvert détecté sur {target} ({ip})"
    except Exception as e:
        return f"Erreur lors du port scan : {e}"



def search_username(username, show_progress=True):
    try:
        sites = {
            "GitHub": f"https://github.com/{username}",
            "Twitter": f"https://twitter.com/{username}",
            "Reddit": f"https://www.reddit.com/user/{username}",
            "Instagram": f"https://www.instagram.com/{username}",
            "Facebook": f"https://www.facebook.com/{username}",
            "LinkedIn": f"https://www.linkedin.com/in/{username}",
            "TikTok": f"https://www.tiktok.com/@{username}",
            "Pinterest": f"https://www.pinterest.com/{username}",
            "Tumblr": f"https://{username}.tumblr.com",
            "Stack Overflow": f"https://stackoverflow.com/users/{username}",
            "Medium": f"https://medium.com/@{username}",
            "Telegram": f"https://t.me/{username}",
            "Snapchat": f"https://www.snapchat.com/add/{username}",
            "Dribbble": f"https://dribbble.com/{username}",
            "Behance": f"https://www.behance.net/{username}",
            "Flickr": f"https://www.flickr.com/people/{username}",
            "SoundCloud": f"https://soundcloud.com/{username}",
            "Vimeo": f"https://vimeo.com/{username}",
            "DeviantArt": f"https://www.deviantart.com/{username}",
            "Goodreads": f"https://www.goodreads.com/{username}",
            "GitLab": f"https://gitlab.com/{username}",
        }

        phone_pattern = re.compile(
            r'(?:(?:\+?\d{1,3}[ \-\.]?)?(?:\(?\d{2}\)?[ \-\.]?)?\d{2}[ \-\.]?\d{2}[ \-\.]?\d{2}[ \-\.]?\d{2})'
        )

        results = []
        iterator = tqdm(sites.items(), desc=f"🔎 Recherche '{username}'", unit="site") if show_progress else sites.items()

        for site, url in iterator:
            try:
                r = requests.get(url, timeout=5, allow_redirects=True)
                if r.status_code == 200:
                    entry = f"✅ Existe sur {site}: {url}"
                    matches = phone_pattern.findall(r.text)

                    cleaned = []
                    for match in matches:
                        num = re.sub(r"[^\d+]", "", match)
                        if len(num) >= 10 and num.startswith(('+', '0')):
                            cleaned.append(num)

                    if cleaned:
                        uniques = sorted(set(cleaned))
                        entry += f"\n   📞 Numéros trouvés : {', '.join(uniques)}"
                elif r.status_code == 404:
                    entry = f"❌ Pas trouvé sur {site}"
                else:
                    entry = f"⚠️ {site} → HTTP {r.status_code}"
            except requests.RequestException as e:
                entry = f"⚠️ Erreur connexion à {site}: {e}"

            results.append(entry)

        return "\n".join(results)

    except Exception as e:
        return f"Erreur lors de la recherche username : {e}"




def get_ssh_banner(host, port=22):
    """
    Tente de se connecter au port SSH (22 par défaut) et lit la bannière du serveur SSH.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect((host, port))
            banner = s.recv(1024).decode().strip()
            return f"Bannière SSH détectée sur {host}:{port} → {banner}"
    except Exception as e:
        return f"Impossible de récupérer la bannière SSH sur {host}:{port} → {e}"
    

def is_vulnerable_ssh(banner):
    """
    Analyse simple de la bannière SSH pour détecter une version vulnérable.
    (Exemple basique, à étendre selon CVE)
    """
    if not banner or "OpenSSH" not in banner:
        return False, "Bannière non reconnue ou absente"

    # Extraction version, ex: OpenSSH_7.4p1 Debian-10+deb9u7
    match = re.search(r"OpenSSH_(\d+)\.(\d+)", banner)
    if not match:
        return False, "Version OpenSSH non détectée"

    major, minor = int(match.group(1)), int(match.group(2))

    # Exemple simple : OpenSSH < 7.6 considéré vulnérable (exemple)
    if major < 7 or (major == 7 and minor < 6):
        return True, f"Version vulnérable détectée : OpenSSH {major}.{minor}"
    else:
        return False, f"Version récente détectée : OpenSSH {major}.{minor}"

def scan_ssh_advanced(host, ports=[22, 2222, 2200, 8022], show_progress=True):
    results = []
    iterator = tqdm(ports, desc="🔑 Scan SSH avancé", unit="port") if show_progress else ports
    for port in iterator:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(2)
                s.connect((host, port))
                banner = s.recv(1024).decode().strip()
                vuln, message = is_vulnerable_ssh(banner)
                results.append(f"Port {port} ouvert - Bannière : {banner}\n  -> {message}")
        except Exception:
            results.append(f"Port {port} fermé ou non SSH")

    return "\n".join(results)

def run_dirscan(target_url, wordlist_path, verbose=False):
    try:
        with open(wordlist_path, "r") as file:
            paths = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        return f"[!] Wordlist introuvable : {wordlist_path}"

    print(f"[+] Ciblage : {target_url}")
    print(f"[+] Wordlist : {wordlist_path}")
    print(f"[+] Démarrage...\n")

    found = []

    iterator = tqdm(paths, desc="Scanning", unit="URL", dynamic_ncols=True)

    for path in iterator:
        url = f"{target_url.rstrip('/')}/{path}"
        try:
            response = requests.get(url, timeout=5)
            if response.status_code in [200, 301, 302, 403]:
                found.append((url, response.status_code))
                if verbose:
                    print(f"[{response.status_code}] {url}")
        except requests.RequestException:
            continue

    if not verbose:
        if found:
            print("\n[+] Chemins valides trouvés :")
            for url, code in found:
                print(f"  [{code}] {url}")
        else:
            print("\n[-] Aucun chemin valide trouvé.")

    return f"\n[✓] Scan terminé. {len(found)} résultats sur {len(paths)} chemins testés."