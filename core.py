"""France company leads from the official Recherche d'entreprises API (no proxy, no scraping)."""
import json, time, urllib.parse, urllib.request

API = 'https://recherche-entreprises.api.gouv.fr/search'
SIZES = {'NN': 'unknown', '00': '0', '01': '1-2', '02': '3-5', '03': '6-9', '11': '10-19', '12': '20-49',
         '21': '50-99', '22': '100-199', '31': '200-249', '32': '250-499', '41': '500-999', '42': '1000-1999',
         '51': '2000-4999', '52': '5000-9999', '53': '10000+'}


def _list(v):
    if v is None: return []
    if isinstance(v, str): v = v.replace(';', ',').split(',')
    return [str(x).strip() for x in v if str(x).strip()]


def build_params(inp):
    """Map Actor input to API query params. Returns (params, error)."""
    p = {'per_page': 25, 'limite_matching_etablissements': 10}
    if inp.get('query'): p['q'] = inp['query'].strip()
    naf = [c.upper() for c in _list(inp.get('nafCodes'))]
    if naf: p['activite_principale'] = ','.join(naf)
    for key, api in (('departments', 'departement'), ('postalCodes', 'code_postal'), ('sizeCodes', 'tranche_effectif_salarie'), ('legalForms', 'nature_juridique')):
        vals = _list(inp.get(key))
        if vals: p[api] = ','.join(vals)
    if inp.get('section'): p['section_activite_principale'] = inp['section'].strip().upper()
    if inp.get('companyCategory'): p['categorie_entreprise'] = inp['companyCategory']
    if inp.get('onlyActive', True): p['etat_administratif'] = 'A'
    if inp.get('excludeSoleTraders', True): p['est_entrepreneur_individuel'] = 'false'
    for key, api in (('revenueMin', 'ca_min'), ('revenueMax', 'ca_max')):
        if inp.get(key) not in (None, ''): p[api] = int(inp[key])
    for key, api in (('onlyRGE', 'est_rge'), ('onlyQualiopi', 'est_qualiopi'), ('onlyESS', 'est_ess')):
        if inp.get(key): p[api] = 'true'
    filters = set(p) - {'per_page', 'limite_matching_etablissements', 'etat_administratif', 'est_entrepreneur_individuel'}
    if not filters:
        return None, 'Give at least one filter: query, nafCodes, section, departments, postalCodes, sizeCodes, revenue or a label flag.'
    return p, None


def fetch(params, page, retries=4):
    url = API + '?' + urllib.parse.urlencode({**params, 'page': page})
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'frix-france-company-leads/1.0 (Apify Actor)'})
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code == 429 or e.code >= 500: time.sleep(2 * (i + 1)); continue
            raise
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 * (i + 1))
    raise RuntimeError('Recherche d\'entreprises API unavailable after retries')


def _finance(c):
    fin = c.get('finances') or {}
    if not fin: return None, None, None
    year = max(fin)
    return year, fin[year].get('ca'), fin[year].get('resultat_net')


def _place(e):
    return {
        'siret': e.get('siret'), 'address': e.get('adresse'), 'postalCode': e.get('code_postal'),
        'city': e.get('libelle_commune'), 'department': (e.get('departement') or (e.get('code_postal') or '')[:2]) or None,
        'latitude': float(e['latitude']) if e.get('latitude') else None,
        'longitude': float(e['longitude']) if e.get('longitude') else None,
        'tradeNames': e.get('liste_enseignes') or ([e['nom_commercial']] if e.get('nom_commercial') else []),
        'establishmentCreated': e.get('date_creation'), 'isHeadquarters': bool(e.get('est_siege')),
    }


def rows(company, per_establishment, inp):
    """Yield output rows for one company; companies that object to commercial prospecting are skipped."""
    if company.get('opposition_diffusion_commerciale') or company.get('statut_diffusion') != 'O':
        return
    if inp.get('excludeSoleTraders', True) and str(company.get('nature_juridique', '')).startswith('1'):
        return
    created_after = inp.get('createdAfter')
    if created_after and (company.get('date_creation') or '') < created_after:
        return
    year, ca, net = _finance(company)
    base = {
        'siren': company['siren'], 'name': company.get('nom_complet'), 'legalName': company.get('nom_raison_sociale'),
        'nafCode': company.get('activite_principale'), 'section': company.get('section_activite_principale'),
        'legalForm': company.get('nature_juridique'), 'category': company.get('categorie_entreprise'),
        'employees': SIZES.get(company.get('tranche_effectif_salarie') or 'NN', company.get('tranche_effectif_salarie')),
        'companyCreated': company.get('date_creation'), 'active': company.get('etat_administratif') == 'A',
        'establishments': company.get('nombre_etablissements_ouverts'),
        'financeYear': year, 'revenue': ca, 'netResult': net,
        'isRGE': bool((company.get('complements') or {}).get('est_rge')),
        'isQualiopi': bool((company.get('complements') or {}).get('est_qualiopi')),
        'vatNumber': company.get('tva'),
        'annuaireUrl': f"https://annuaire-entreprises.data.gouv.fr/entreprise/{company['siren']}",
    }
    places = company.get('matching_etablissements') if per_establishment else None
    if places:
        for e in places:
            if inp.get('onlyActive', True) and e.get('etat_administratif') not in (None, 'A'): continue
            yield {**base, **_place(e)}
    else:
        yield {**base, **_place(company.get('siege') or {})}
