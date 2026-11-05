import asyncio
from apify import Actor
from core import build_params, fetch, rows


async def main():
    async with Actor:
        inp = await Actor.get_input() or {}
        params, err = build_params(inp)
        if err:
            await Actor.fail(status_message=err); return
        limit = max(1, min(int(inp.get('maxResults') or 100), 10000))
        per_est = inp.get('outputMode', 'establishments') == 'establishments'
        seen, pushed, page = set(), 0, 1
        while pushed < limit:
            data = await asyncio.to_thread(fetch, params, page)
            results = data.get('results') or []
            if page == 1:
                Actor.log.info(f"{data.get('total_results', 0)} companies match the filters")
            for c in results:
                for row in rows(c, per_est, inp):
                    key = row.get('siret') or row['siren']
                    if key in seen: continue
                    seen.add(key)
                    res = await Actor.push_data(row, charged_event_name='lead')
                    pushed += 1
                    if (res and res.event_charge_limit_reached) or pushed >= limit: break
                if pushed >= limit: break
            if page >= (data.get('total_pages') or 1) or page * 25 >= 10000: break
            page += 1
            await asyncio.sleep(0.25)  # stay well below the API's 7 requests/second
        await Actor.set_status_message(f'{pushed} leads saved')

if __name__ == '__main__':
    asyncio.run(main())
