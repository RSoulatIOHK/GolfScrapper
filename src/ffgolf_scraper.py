import requests
from bs4 import BeautifulSoup
import pandas as pd
from urllib.parse import urljoin
import re
import time
import argparse

# ANSI color codes
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Regular colors
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

    # Background colors
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_YELLOW = '\033[103m'

def print_colored(text, color=Colors.RESET, bold=False):
    """Print colored text."""
    prefix = Colors.BOLD if bold else ""
    print(f"{prefix}{color}{text}{Colors.RESET}")

def print_error(text, indent=0):
    """Print error message with indentation."""
    indentation = "  " * indent
    print_colored(f"{indentation}⚠ {text}", Colors.YELLOW)

def print_success(text, indent=0):
    """Print success message with indentation."""
    indentation = "  " * indent
    print_colored(f"{indentation}✓ {text}", Colors.GREEN)

def print_info(text, color=Colors.CYAN, indent=0):
    """Print info message with indentation."""
    indentation = "  " * indent
    print_colored(f"{indentation}{text}", color)


class FFGolfScrapper:
    def __init__(self, delay=0.5, max_golfs=None, max_regions=None, output_file="golfs_france.xlsx"):
        """ Initialize the scrapper with base URL and headers. """
        self.base_url = "https://www.ffgolf.org"
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "FFGolf-Scraper/1.0"
        }
        self.golfs_data = []
        self.config = {
            "delay_between_requests": delay,
            "max_golfs_per_region": max_golfs,
            "max_regions": max_regions,
            "output_file": output_file
        }

    def get_page(self, url: str) -> BeautifulSoup:
        """ Fetch the HTML content of a page and return a BeautifulSoup object. """
        try:
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return BeautifulSoup(response.content, "html.parser")
        except requests.RequestException as e:
            print_error(f"Error fetching {url}: {e}", indent=1)
            return None

    def get_regions(self) -> list[dict]:
        """ Extract the list of French regions from the main page. """
        url = "https://www.ffgolf.org/parcours-detours/guide-des-golfs"
        soup = self.get_page(url)
        if not soup:
            return []
        regions = []
        region_links = soup.find_all('a', href=re.compile(r'/parcours-detours/guide-des-golfs/[^/]+$'))
        for link in region_links:
            href = link.get('href')
            if href:
                region_url = urljoin(self.base_url, href)
                region_name = link.text.strip() or href.split('/')[-1]
                regions.append(
                    {'name': region_name, 'url': region_url})
        return regions

    def get_golfs_from_region(self, region_url: str) -> list[dict]:
        """ Extract golf courses from a region page. """
        soup = self.get_page(region_url)
        if not soup:
            return []
        golfs = []
        golf_links = soup.find_all('a', href=re.compile(r'/parcours-detours/guide-des-golfs/[^/]+'))
        for link in golf_links:
            if "login" in link.get('href', ''):
                continue
            if "search" in link.get('href', ''):
                continue
            href = link.get('href')
            if href:
                golf_url = urljoin(self.base_url, href)
                if golf_url not in [g['url'] for g in golfs]:
                    golfs.append({
                        'name': link.text.strip(),
                        'url': golf_url
                    })
        return golfs

    def extract_golf_details(self, golf_url: str) -> dict:
        """ Extract detailed information about a golf course. """
        soup = self.get_page(golf_url)
        if not soup:
            return {}
        details = {
            'nom': '',
            'adresse': '',
            'code_postal': '',
            'ville': '',
            'telephone': '',
            'email': '',
            'site_web': '',
            'url_ffgolf': golf_url
        }

        title = soup.find('h1')
        if title:
            details['nom'] = title.text.strip()

        page_text = soup.get_text()

        # Track missing fields
        missing_fields = []

        # Adresse
        adresse_match = re.search(r'adresse\s*:\s*(.+?)(?=téléphone|e-mail|site web|$)', page_text, re.IGNORECASE | re.DOTALL)
        if adresse_match:
            adresse_raw = adresse_match.group(1).strip()
            # Clean up: remove excessive whitespace and newlines
            adresse_complete = re.sub(r'\s+', ' ', adresse_raw).strip()
            
            # print(f"Debug adresse_complete: '{adresse_complete}'")
            
            # Look for postal code (5 digits) and city
            # Try pattern: anything + 5 digits + city name
            cp_ville_match = re.search(r'(.+?)\s+(\d{5})\s+([A-ZÀ-Ÿ][A-ZÀ-Ÿ\s\-]+)$', adresse_complete)
            
            if cp_ville_match:
                # print(f"Debug cp_ville_match: {cp_ville_match.groups()}")
                details['adresse'] = cp_ville_match.group(1).strip()
                details['code_postal'] = cp_ville_match.group(2)
                details['ville'] = cp_ville_match.group(3).strip()
            else:
                # Fallback: store the whole thing in adresse
                details['adresse'] = adresse_complete
        else:
            missing_fields.append('adresse')

        telephone_match = re.search(r'téléphone\s*:\s*([^\n]+)', page_text, re.IGNORECASE)
        if telephone_match:
            details['telephone'] = telephone_match.group(1).strip()
        else:
            missing_fields.append('téléphone')

        email_match = re.search(r'e-mail\s*:\s*([^\n]+)', page_text, re.IGNORECASE)
        if email_match:
            details['email'] = email_match.group(1).strip()
        else:
            missing_fields.append('e-mail')

        site_web_match = re.search(r'site web\s*:\s*([^\n]+)', page_text, re.IGNORECASE)
        if site_web_match:
            details['site_web'] = site_web_match.group(1).strip()
        else:
            missing_fields.append('site web')

        # Print missing fields if any
        if missing_fields:
            print_error(f"Champs manquants pour {golf_url}: {', '.join(missing_fields)}", indent=2)

        return details

    def scrape_all_golfs(self) -> None:
        """ Scrape all golf courses from all regions and store in golfs_data. """
        print_info("Récupération des régions...", Colors.CYAN, indent=0)
        regions = self.get_regions()

        if not regions:
            print_error("Aucune région trouvée. Êtes-vous sûr de l'URL de base ?", indent=0)
            return

        print_success(f"{len(regions)} régions trouvées.", indent=0)

        for j, region in enumerate(regions, start=1):
            print_colored(f"\n[{j}/{len(regions)}] Récupération des golfs pour la région: {region['name']}", Colors.BLUE, bold=True)
            golfs = self.get_golfs_from_region(region['url'])
            print_info(f"{len(golfs)} golfs trouvés dans la région {region['name']}.", Colors.CYAN, indent=1)

            for i, golf in enumerate(golfs, start=1):
                golf_info = self.extract_golf_details(golf['url'])
                print_info(f"[{i}/{len(golfs)}] Extraction: {golf_info.get('nom', golf['name'])}", Colors.WHITE, indent=1)

                if golf_info:
                    golf_info['region'] = region['name']
                    self.golfs_data.append(golf_info)
                else:
                    print_error(f"Erreur lors de l'extraction pour {golf['name']}", indent=2)

                time.sleep(self.config['delay_between_requests'])

                if self.config['max_golfs_per_region'] and i >= self.config['max_golfs_per_region']:
                    break

            if self.config['max_regions'] and j >= self.config['max_regions']:
                break

        print_colored(f"\n{'='*60}", Colors.CYAN)
        print_success(f"Total: {len(self.golfs_data)} golfs extraits.", indent=0)
        print_colored(f"{'='*60}", Colors.CYAN)

    def save_to_excel(self, filename: str) -> None:
        """ Save the scraped golf data to an Excel file. """
        if not self.golfs_data:
            print_error("Aucune donnée à sauvegarder.", indent=0)
            return

        df = pd.DataFrame(self.golfs_data)

        columns_order = ['region', 'nom', 'adresse', 'code_postal', 'ville', 'telephone', 'email', 'site_web', 'url_ffgolf']
        df = df.reindex(columns=columns_order)
        df.to_excel(filename, index=False, engine='openpyxl')

        print_colored(f"\n{'='*60}", Colors.GREEN)
        print_success(f"Données sauvegardées dans {filename}", indent=0)
        print_info(f"Nombre de golfs: {len(df)}", Colors.GREEN, indent=1)
        print_info(f"Régions couvertes: {df['region'].nunique()}", Colors.GREEN, indent=1)

def main():
    """ Fonction principale pour exécuter le scrapper. """
    parser = argparse.ArgumentParser(
        description='Scraper pour extraire les informations des golfs en France depuis le site de la FFGolf.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemples d'utilisation:
  # Mode test (2 régions, 5 golfs par région) - DÉFAUT
  python ffgolf_scraper.py
  python ffgolf_scraper.py --test

  # Scraper toutes les régions et tous les golfs
  python ffgolf_scraper.py --all

  # Limiter à 3 régions avec tous les golfs
  python ffgolf_scraper.py --max-regions 3

  # Limiter à 10 golfs pour toutes les régions
  python ffgolf_scraper.py --max-golfs 10

  # Limiter à 3 régions et 10 golfs par région
  python ffgolf_scraper.py --max-regions 3 --max-golfs 10

  # Changer le délai entre les requêtes à 2 secondes
  python ffgolf_scraper.py --all --delay 2

  # Spécifier un nom de fichier de sortie personnalisé
  python ffgolf_scraper.py --all --output golfs_custom.xlsx
        """
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Mode test avec 2 régions et 5 golfs par région (mode par défaut).'
    )

    parser.add_argument(
        '--all',
        action='store_true',
        help='Scraper toutes les régions et tous les golfs.'
    )

    parser.add_argument(
        '--max-regions',
        type=int,
        default=None,
        metavar='N',
        help='Nombre maximum de régions à scraper.'
    )

    parser.add_argument(
        '--max-golfs',
        type=int,
        default=None,
        metavar='N',
        help='Nombre maximum de golfs par région à scraper.'
    )

    parser.add_argument(
        '--delay',
        type=float,
        default=0.5,
        metavar='SECONDS',
        help='Délai entre les requêtes en secondes (défaut: 0.5).'
    )

    parser.add_argument(
        '--output',
        type=str,
        default='golfs_france.xlsx',
        metavar='FILENAME',
        help='Nom du fichier de sortie Excel (défaut: golfs_france.xlsx).'
    )

    args = parser.parse_args()

    # Déterminer les limites selon les arguments
    max_regions = None
    max_golfs = None

    print_colored("\n" + "="*60, Colors.MAGENTA, bold=True)

    if args.all:
        # Mode complet: pas de limites
        print_colored("Mode: Scraping complet", Colors.MAGENTA, bold=True)
        print_info("  - Toutes les régions", Colors.CYAN)
        print_info("  - Tous les golfs par région", Colors.CYAN)
        max_regions = None
        max_golfs = None

    elif args.max_regions or args.max_golfs:
        # Mode personnalisé avec limites spécifiques
        max_regions = args.max_regions
        max_golfs = args.max_golfs
        print_colored("Mode: Personnalisé", Colors.MAGENTA, bold=True)
        if max_regions:
            print_info(f"  - Maximum {max_regions} région(s)", Colors.CYAN)
        else:
            print_info("  - Toutes les régions", Colors.CYAN)
        if max_golfs:
            print_info(f"  - Maximum {max_golfs} golf(s) par région", Colors.CYAN)
        else:
            print_info("  - Tous les golfs par région", Colors.CYAN)

    else:
        # Mode test par défaut (sécurisé)
        max_regions = 2
        max_golfs = 5
        print_colored("Mode: Test (défaut)", Colors.YELLOW, bold=True)
        print_info("  - 2 régions maximum", Colors.CYAN)
        print_info("  - 5 golfs maximum par région", Colors.CYAN)
        print_colored("\n  ℹ  Utilisez --all pour scraper toutes les données", Colors.BLUE)

    print_info(f"\nDélai entre les requêtes: {args.delay} seconde(s)", Colors.WHITE)
    print_info(f"Fichier de sortie: {args.output}", Colors.WHITE)
    print_colored("="*60 + "\n", Colors.MAGENTA, bold=True)

    # Créer l'instance du scraper avec la configuration
    scrapper = FFGolfScrapper(
        delay=args.delay,
        max_golfs=max_golfs,
        max_regions=max_regions,
        output_file=args.output
    )

    # Exécuter le scraping
    scrapper.scrape_all_golfs()

    # Sauvegarder les résultats
    scrapper.save_to_excel(scrapper.config['output_file'])
    print_colored("✓ Scraping terminé avec succès!", Colors.GREEN, bold=True)
    if args.test or (not args.all and not args.max_regions and not args.max_golfs):
        print_colored("⚠ Mode test activé. Utilisez --all pour scraper toutes les données.", Colors.YELLOW, bold=True)
    print_colored("="*60 + "\n", Colors.GREEN, bold=True)


if __name__ == "__main__":
    main()