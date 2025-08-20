OSINTPlus


    Un outil OSINT simple et polyvalent, utilisable en ligne de commande ou directement dans vos scripts Python — le tout sans utiliser d'API.

# 🧠 Description

OSINTPlus est un outil en ligne de commande pour effectuer des recherches OSINT complètes sur des domaines, hôtes et sites web, sans nécessiter de clés API. Il peut également être utilisé comme une bibliothèque Python, intégrable dans vos projets de pentesting, automatisation ou recherche.

Il propose diverses fonctionnalités : résolution DNS, ping, WHOIS, scan de ports, récupération de données web (headers, liens, contenu, etc.), analyse SSH, détection de technologies, recherche de pseudo, brute-force de répertoires, et plus encore.


# ⚙️ Fonctionnalités

Fonctionnalités principales

    * 🔍 Résolution DNS et WHOIS

    * 📡 Ping & scan de ports TCP

    * 🌐 Analyse HTTP (headers, robots.txt, favicon, technologies, liens, contenu)

    * 🔐 Scan SSH & récupération de bannière

    * 🧑‍💻 Recherche de pseudo sur les réseaux

    * 📁 Brute-force de répertoires (dirscan)

    * 📤 Export des résultats (JSON / TXT)

    * 🧩 Utilisable en CLI et comme module Python


# 🚀 Installation

    git clone https://github.com/hakersgenie/osintplus
    cd osintplus

    pip install osintplus


# 🖥️ Utilisation en ligne de commande (CLI)

Exemples d’utilisation des différentes options :

    * osintplus --domain example.com
    * osintplus --ping example.com
    * osintplus --whois example.com
    * osintplus --headers http://example.com
    * osintplus --robots example.com
    * osintplus --favicon example.com
    * osintplus --tech http://example.com
    * osintplus --links http://example.com
    * osintplus --content http://example.com
    * osintplus --sshadv example.com
    * osintplus --sshbanner example.com
    * osintplus --portscan example.com,1-1024
    * osintplus --username monpseudo
    * osintplus --dirscan http://example.com --wordlist ./wordlists/common.txt
    * osintplus --export results.json
    * osintplus --whois example.com --verbose

# 🐍 Utilisation dans un script Python

Tu peux aussi importer OSINTPlus dans tes propres scripts :

    from osintplus.core import resolve_domain

# Résolution DNS
    ip = resolve_domain("example.com")
    print(f"IP de example.com : {ip}")

# WHOIS
    whois_data = get_whois_info("example.com")
    print(whois_data)

# Scan de ports
    open_ports = port_scan("example.com", ports=range(1, 1024))
    print(open_ports)

L’interface exacte dépend de ta structure interne (tools.py, utils.py, etc.). Il faudra adapter selon ton code.

# 🧾 Export des résultats

    * Ajoute --export fichier.json ou --export fichier.txt pour sauvegarder les résultats.

# 📚 Pré-requis

Python 3.6+

Modules Python requis (automatiquement installés avec pip install osintplus)

    * tqdm
    * colorama
    * requests
    * python-whois

# 🤝 Contribution

Les contributions sont les bienvenues ! N’hésitez pas à ouvrir une issue ou pull request.

#  📄 Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE.md)

📬 Contact

  * GitHub : @hakersgenie
  * Email : hakersgenie@gmail.com