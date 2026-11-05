# France Company Leads Finder (SIRENE, official API)

Build a list of **French companies by activity, area and size** in a few seconds: hairdressers in Lyon, restaurants in Paris 11e, plumbers in Gironde, RGE-certified builders in Brittany, training centres with Qualiopi…

The Actor queries the **official French government company directory** (*Recherche d'entreprises*, data from INSEE SIRENE and the RNE). No scraping, no proxy, no login, so runs are fast, cheap and stable.

## What you get

One row per **local branch** (établissement) that matches your filters, or one row per company (headquarters):

| Field | Example |
|---|---|
| `name`, `legalName`, `tradeNames` | ACCESS NAILS, ["ACCESS NAILS"] |
| `nafCode`, `section` | 96.02B, S |
| `address`, `postalCode`, `city`, `department` | 12 RUE …, 95880, ENGHIEN-LES-BAINS, 95 |
| `latitude`, `longitude` | 48.97, 2.30 |
| `siren`, `siret`, `vatNumber` | 9-digit SIREN, 14-digit SIRET, FR VAT |
| `employees`, `category` | 6-9, PME |
| `revenue`, `netResult`, `financeYear` | 197448, …, 2024 (when accounts are published) |
| `companyCreated`, `establishmentCreated` | 2019-03-01 |
| `isRGE`, `isQualiopi`, `active` | true / false |
| `annuaireUrl` | link to the official company page |

Export to CSV, Excel, JSON, or send it straight to Google Sheets, HubSpot or Make/Zapier with Apify integrations.

## Filters

- **Keyword**: matched on company and trade names (`"boulangerie"`, `"garage"`).
- **NAF/APE codes**: e.g. `56.10A` restaurants, `56.10C` fast food, `96.02A` hairdressers, `96.02B` beauty salons, `45.20A` car repair, `43.22A` plumbing/heating, `43.21A` electricians, `68.31Z` real-estate agencies, `86.23Z` dentists, `69.20Z` accountants.
- **Departments** and **postal codes**.
- **Employee range**, **company category** (PME/ETI/GE), **revenue min/max**.
- **Created after** a date, to target new companies.
- **Labels**: RGE (energy renovation), Qualiopi (training), ESS.

Up to 10,000 results per run.

## Example input

```json
{
  "nafCodes": ["96.02A", "96.02B"],
  "departments": ["69"],
  "outputMode": "establishments",
  "maxResults": 500
}
```

## Who uses it

- Web agencies, accountants, insurers and SaaS sales teams building local prospect lists.
- Market studies: how many bakeries per department, where new restaurants open.
- Enriching a CRM with SIRET, VAT number, NAF code and employee range.

## Privacy and compliance

- **Sole traders (natural persons) are excluded by default.**
- Companies that **object to commercial prospecting** (`opposition_diffusion_commerciale`) or are not publicly disseminated are **always skipped**.
- No director names, birth dates or personal contact details are returned.
- You remain responsible for how you use the data (GDPR, French rules on B2B prospecting). Data comes from the open *API Recherche d'entreprises* (Etalab Open Licence 2.0).

## Pricing

Pay per result: you only pay for leads saved to the dataset. Platform usage is included.

## Limits

- The official API returns at most 10,000 companies per query; split by department for bigger lists.
- Revenue is only present when the company published its accounts.
- No phone numbers or emails (the official directory does not publish them). Pair it with a website/contact enrichment Actor if you need them.

Made by [Frix Studio](https://frix-studio.vercel.app). Questions or a custom field? Open an issue on the Actor page.
