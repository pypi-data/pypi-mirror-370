import argparse
from osintplus.utils import banner
from osintplus.core import run_dirscan

from osintplus.core import (
    resolve_domain,
    ping_host,
    get_whois_info,
    get_headers,
    get_robots_txt,
    get_favicon_hash,
    detect_technologies,
    get_links,
    get_content_summary,
    port_scan,
    search_username,
    get_ssh_banner,
    scan_ssh_advanced
)


def main():

    try:

        print(banner())

        parser = argparse.ArgumentParser(description="Outil OSINTPLUS CLI")

        # Définition des arguments
        parser.add_argument("--domain", help="Résoudre un domaine en IP", metavar="")
        parser.add_argument("--ping", help="Pinger un hôte", metavar="")
        parser.add_argument("--whois", help="Informations WHOIS", metavar="")
        parser.add_argument("--headers", help="Voir les headers HTTP", metavar="")
        parser.add_argument("--robots", help="Voir le fichier robots.txt", metavar="")
        parser.add_argument("--favicon", help="Télécharger et hasher favicon.ico", metavar="")
        parser.add_argument("--tech", help="Détecter technologies d’un site", metavar="")
        parser.add_argument("--links", help="Lister tous les liens d’une page", metavar="")
        parser.add_argument("--content", help="Récupérer titre et H1 d’une page", metavar="")
        parser.add_argument("--sshadv", help="Scan avancé SSH (ex: example.com)", metavar="")
        parser.add_argument("--sshbanner", help="Récupère la bannière SSH d'un hôte", metavar="")
        parser.add_argument("--portscan", help="Scanner les ports TCP (ex: example.com,1-1024)", metavar="")
        parser.add_argument("--username", help="Recherche un pseudo sur sites populaires", metavar="")
        parser.add_argument("--export", help="Fichier de sauvegarde des résultats (txt/json)", metavar="")
        parser.add_argument("--dirscan", help="Brute-force des répertoires/fichiers d'un site", metavar="")
        parser.add_argument("--wordlist", help="Fichier de wordlist (défaut: ./wordlists/common.txt)", metavar="")
        parser.add_argument("--verbose", help="Afficher chaque résultat pendant le scan", action="store_true")




        args = parser.parse_args()

        if args.domain:
            print(resolve_domain(args.domain))
        elif args.ping:
            print(ping_host(args.ping))
        elif args.whois:
            print(get_whois_info(args.whois))
        elif args.headers:
            print(get_headers(args.headers))
        elif args.robots:
            print(get_robots_txt(args.robots))
        elif args.favicon:
            print(get_favicon_hash(args.favicon))
        elif args.tech:
            print(detect_technologies(args.tech))
        elif args.links:
            print(get_links(args.links))
        elif args.content:
            print(get_content_summary(args.content))
        elif args.portscan:
            parts = args.portscan.split(",")
            target = parts[0]
            port_range = parts[1] if len(parts) > 1 else None
            print(port_scan(target, port_range))
        elif args.username:
            print(search_username(args.username, export_file=args.export))
        elif args.sshbanner:
            print(get_ssh_banner(args.sshbanner))
        elif args.sshadv:
            print(scan_ssh_advanced(args.sshadv))
        elif args.dirscan:
            wordlist_path = args.wordlist if args.wordlist else "./wordlists/common.txt"
            print(run_dirscan(args.dirscan, wordlist_path, verbose=args.verbose))
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n[!] Interruption par l'utilisateur. Fin du programme.")

if __name__ == "__main__":
    main()
