#!/usr/bin/env python3
"""Fetch public GitHub activity and draw repository-owned profile graphics.

GITHUB_TOKEN (or GH_TOKEN) is required for live GraphQL. --snapshot replays a
previous response offline. Dates use UTC; never substitute invented activity.
"""
import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import textwrap
import time
import urllib.error
import urllib.request

from svg import ROOT, esc, line, rect, text, write_pair
from features import draw_pulse, project_notes, project_index
from observatory import draw_atlas, draw_milestones, comparison, discovery

REPOS = '''query($login:String!, $cursor:String) {
 user(login:$login) { repositories(first:100,after:$cursor,privacy:PUBLIC,
 isFork:false,ownerAffiliations:OWNER,orderBy:{field:PUSHED_AT,direction:DESC}) {
 pageInfo {hasNextPage endCursor}
 nodes {name description url pushedAt isArchived isEmpty primaryLanguage{name}
 hasIssuesEnabled
 latestRelease {tagName url publishedAt isDraft}
 defaultBranchRef {name target {... on Commit {messageHeadline committedDate url}}}
 languages(first:100) {pageInfo{hasNextPage endCursor} edges{size node{name}}}}
 }}}'''
CALENDAR = '''query($login:String!, $from:DateTime!, $to:DateTime!) {
 user(login:$login) { contributionsCollection(from:$from,to:$to) {
 contributionCalendar {weeks {contributionDays {date contributionCount}}}
 }}}'''
LANGUAGES = '''query($login:String!,$name:String!,$cursor:String) {
 repository(owner:$login,name:$name) {languages(first:100,after:$cursor) {
 pageInfo{hasNextPage endCursor} edges{size node{name}}}}}'''


def graphql(query, variables, token):
    payload = json.dumps({'query': query, 'variables': variables}).encode()
    for attempt in range(4):
        request = urllib.request.Request('https://api.github.com/graphql', data=payload, headers={
            'Authorization': f'Bearer {token}', 'User-Agent': 'repository-profile-generator',
            'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(request, timeout=45) as response:
                result = json.load(response)
            if result.get('errors'):
                raise RuntimeError('GitHub GraphQL: ' + '; '.join(e['message'] for e in result['errors']))
            return result['data']
        except urllib.error.HTTPError as error:
            if error.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise RuntimeError(f'GitHub API HTTP {error.code}; previous graphics were preserved.') from None
        except (urllib.error.URLError, TimeoutError):
            if attempt == 3:
                raise RuntimeError('GitHub API unreachable; previous graphics were preserved.') from None
        time.sleep(2 ** attempt)
    raise RuntimeError('GitHub API unavailable')


def fetch(login, today, token):
    start = today - timedelta(days=364)
    variables = {'login': login, 'from': f'{start}T00:00:00Z', 'to': f'{today}T23:59:59Z'}
    user = graphql(CALENDAR, variables, token)['user']
    if user is None:
        raise ValueError(f'GitHub user {login} does not exist')
    days = sorted(({'date': d['date'], 'count': d['contributionCount']}
                   for w in user['contributionsCollection']['contributionCalendar']['weeks']
                   for d in w['contributionDays'] if str(start) <= d['date'] <= str(today)), key=lambda d: d['date'])
    repos, cursor = [], None
    while True:
        connection = graphql(REPOS, {'login': login, 'cursor': cursor}, token)['user']['repositories']
        for repo in connection['nodes']:
            # Exclude this generated repository from code-size totals and recent work.
            if repo['name'].casefold() == login.casefold() or repo['isEmpty']:
                continue
            languages = repo['languages']
            edges = list(languages['edges'])
            while languages['pageInfo']['hasNextPage']:
                languages = graphql(LANGUAGES, {'login': login, 'name': repo['name'],
                    'cursor': languages['pageInfo']['endCursor']}, token)['repository']['languages']
                edges.extend(languages['edges'])
            branch = repo.get('defaultBranchRef') or {}
            commit = branch.get('target') or {}
            release = repo.get('latestRelease')
            if release and release.get('isDraft'):
                release = None
            repos.append({'name': repo['name'], 'description': repo['description'] or '',
                'url': repo['url'], 'pushed': (repo['pushedAt'] or '')[:10],
                'archived': repo['isArchived'], 'pushed_at': repo['pushedAt'] or '',
                'primary': (repo['primaryLanguage'] or {}).get('name', 'Unclassified'),
                'branch': branch.get('name'), 'issues_enabled': repo['hasIssuesEnabled'],
                'latest_commit': {'headline':commit['messageHeadline'], 'date':commit['committedDate'][:10], 'url':commit['url']} if commit.get('messageHeadline') else None,
                'release': {'tag':release['tagName'],'date':release['publishedAt'][:10],'url':release['url']} if release else None,
                'languages': {e['node']['name']: e['size'] for e in edges}})
        if not connection['pageInfo']['hasNextPage']:
            break
        cursor = connection['pageInfo']['endCursor']
    return {'schema': 1, 'login': login, 'as_of': str(today), 'days': days,
            'repositories': sorted(repos, key=lambda r: r['name'].casefold())}


def validate_data(data):
    today = date.fromisoformat(data['as_of'])
    expected = [str(today - timedelta(days=n)) for n in range(364, -1, -1)]
    if [d['date'] for d in data['days']] != expected:
        raise ValueError('Expected exactly 365 consecutive contribution days; refusing partial data')
    if any(type(d['count']) is not int or d['count'] < 0 for d in data['days']):
        raise ValueError('Invalid contribution count')
    return today


def streaks(days):
    """Current allows today to remain unfinished; longest is within the window."""
    runs, run = [], []
    for day in days:
        if day['count']:
            run.append(day)
        elif run:
            runs.append(run)
            run = []
    if run:
        runs.append(run)
    longest = max(runs, key=len, default=[])
    current = runs[-1] if runs and runs[-1][-1]['date'] in {d['date'] for d in days[-2:]} else []
    return current, longest


def weekly(days):
    buckets = defaultdict(int)
    for day in days:
        dt = date.fromisoformat(day['date'])
        sunday = dt - timedelta(days=(dt.weekday() + 1) % 7)
        buckets[str(sunday)] += day['count']
    return sorted(buckets.items())


def range_label(run):
    return f'{run[0]["date"]} / {run[-1]["date"]}' if run else 'No active run'


def language_totals(repos):
    sizes, counts = Counter(), Counter()
    for repo in repos:
        for name, size in repo['languages'].items():
            if size > 0:
                sizes[name] += size
                counts[name] += 1
    return sizes, counts


def recent_repos(repos):
    return sorted((r for r in repos if not r['archived']), key=lambda r: (r.get('pushed_at',r['pushed']), r['name']), reverse=True)[:4]


def repository_description(repo):
    if repo['description']:
        return repo['description'].strip()
    config = json.loads((ROOT/'profile.json').read_text())
    return config.get('description_fallbacks',{}).get(repo['name'],{}).get('text','No repository description provided.')


def picture(name, alt):
    return (f'<picture>\n  <source media="(prefers-color-scheme: dark)" srcset="generated/{name}-dark.svg">\n'
            f'  <img src="generated/{name}.svg" width="620" alt="{esc(alt)}">\n</picture>')


def render(data, out):
    today = validate_data(data)
    days, repos = data['days'], data['repositories']
    weeks = weekly(days)
    total, active = sum(d['count'] for d in days), sum(bool(d['count']) for d in days)
    peak = max(v for _, v in weeks)
    description = f'{total} contributions across {active} active days. Best Sunday–Saturday week: {peak} contributions. {days[0]["date"]} through {today}, UTC.'
    body = text(0, 16, 'ACTIVITY / LAST 365 DAYS', 10, 'muted') + text(620, 16, str(today) + ' UTC', 10, 'muted', 'end')
    body += text(0, 84, f'{total:,}', 58) + text(0, 110, 'contributions', 12, 'muted')
    body += text(375, 71, str(active), 30) + text(375, 95, 'active days', 11, 'muted')
    body += text(620, 71, str(peak), 30, anchor='end') + text(620, 95, 'best week', 11, 'muted', 'end')
    coords = [(i * 620 / max(1, len(weeks)-1), 184 - v / max(1, peak) * 48) for i, (_, v) in enumerate(weeks)]
    points = ' '.join(f'{x:.2f},{y:.2f}' for x,y in coords)
    body += f'<polygon points="0,188 {points} 620,188" class="soft"/>'
    body += f'<polyline points="{points}" class="stroke" stroke-width="1.5" stroke-linejoin="round"/>' + line(0, 188, 620, 188)
    body += text(0, 210, days[0]['date'], 10, 'muted') + text(310, 210, 'WEEKLY CONTRIBUTIONS', 9, 'muted', 'middle') + text(620, 210, str(today), 10, 'muted', 'end')
    write_pair(out, 'stats', 'A year of building', description, 228, body)

    current, longest = streaks(days)
    body = ''
    for x, title, run in ((0, 'CURRENT STREAK', current), (332, 'LONGEST / LAST 365 DAYS', longest)):
        body += text(x, 16, title, 10, 'muted') + text(x, 67, len(run), 42)
        body += text(x + 83, 66, 'day' if len(run) == 1 else 'days', 12, 'muted') + text(x, 97, range_label(run), 10, 'muted')
    body += line(310, 0, 310, 106) + text(0, 128, 'UTC days · today may still be in progress', 10, 'muted')
    streak_desc = f'Current: {len(current)} {"day" if len(current) == 1 else "days"} ({range_label(current)}). Longest within the last 365 days: {len(longest)} days ({range_label(longest)}).'
    write_pair(out, 'streak', 'Consistency', streak_desc, 149, body)

    sizes, counts = language_totals(repos)
    ordered = sorted(sizes, key=lambda n: (-sizes[n], n))[:6]
    size_total = sum(sizes.values())
    body = text(0, 16, f'{len(repos):02d} PUBLIC REPOSITORIES', 10, 'muted') + text(445, 16, 'CODE SIZE', 10, 'muted', 'end') + text(620, 16, 'REPOS', 10, 'muted', 'end')
    for i, name in enumerate(ordered):
        y = 53 + i * 36
        percent = sizes[name] / size_total * 100
        body += text(0, y, name, 12) + rect(138, y-9, 222, 6, 'soft') + rect(138, y-9, round(222 * percent / 100, 2), 6)
        body += text(445, y, f'{percent:.1f}%', 12, anchor='end') + text(620, y, f'{counts[name]} / {len(repos)}', 12, anchor='end')
    y = 53 + max(1,len(ordered)) * 36
    if not ordered:
        body += text(0, 55, 'No public language data yet.', 12, 'muted')
    remainder = sum(sizes[n] for n in sizes if n not in ordered)
    body += line(0, y-12, 620, y-12) + text(0, y+12, 'Approximate bytes · non-forks · profile repo excluded', 10, 'muted')
    if remainder:
        body += text(0, y+32, f'Other languages: {remainder / size_total * 100:.1f}% of code size', 10, 'muted')
    lang_desc = '; '.join(f'{n}: {sizes[n]:,} bytes ({sizes[n]/size_total:.1%}), {counts[n]} repositories' for n in sorted(sizes, key=lambda n: (-sizes[n], n))) or 'No public language data'
    write_pair(out, 'langs', 'Languages / two perspectives', lang_desc, y+50, body)

    body = text(0, 16, 'ONE CHARACTER / ONE DAY', 10, 'muted')
    origin = date.fromisoformat(weeks[0][0])
    step = 574 / max(1, len(weeks)-1)
    first_month = date.fromisoformat(days[0]['date']).strftime('%b').upper()
    body += text(40,39,first_month,9,'muted')
    last_month = date.fromisoformat(days[0]['date']).month
    calendar_rows = [[' ']*len(weeks) for _ in range(7)]
    for i, day in enumerate(days):
        dt = date.fromisoformat(day['date'])
        column = (dt-origin).days // 7
        row = (dt.weekday()+1) % 7
        x, y = 40 + column*step, 62 + row*18
        if dt.day == 1 and dt.month != last_month:
            body += text(620 if x > 594 else round(x,2), 39, dt.strftime('%b').upper(), 9, 'muted', 'end' if x > 594 else 'start')
            last_month = dt.month
        count = day['count']
        glyph = '.' if not count else ':' if count <= 2 else '+' if count <= 5 else '*' if count <= 10 else '#'
        calendar_rows[row][column] = glyph
    positions = ' '.join(str(round(40+i*step,2)) for i in range(len(weeks)))
    for row, glyphs in enumerate(calendar_rows):
        for active_layer in (False,True):
            values = ''.join(g if ((g not in ' .') == active_layer) else ' ' for g in glyphs)
            body += text(positions,62+row*18,values,13,'ink' if active_layer else 'muted',extra='xml:space="preserve"')
    for row, label in ((1,'M'),(3,'W'),(5,'F')):
        body += text(0, 62+row*18, label, 10, 'muted')
    body += line(0, 190, 620, 190) + text(0, 216, '. 0    : 1–2    + 3–5    * 6–10    # 11+', 10, 'muted')
    body += text(620, 216, 'UTC', 10, 'muted', 'end')
    write_pair(out, 'year', 'The year, in characters', description + ' Rows run Sunday to Saturday; columns run oldest to newest. Dot: zero; colon: 1–2; plus: 3–5; asterisk: 6–10; hash: 11 or more.', 234, body)

    recent = recent_repos(repos)
    body = text(0,16,'LATEST PUBLIC PUSHES',10,'muted') + text(620,16,'REPOSITORY / LANGUAGE',10,'muted','end')
    summaries = []
    for i, repo in enumerate(recent):
        card_start = len(body)
        y = 52 + i * 114
        body += text(0, y, f'{i+1:02d}', 11, 'muted') + text(30, y, textwrap.shorten(repo['name'], width=38, placeholder='…'), 15)
        body += text(620,y,repo['primary'],10,'muted','end')
        desc = repository_description(repo)
        lines = textwrap.wrap(desc, width=76, max_lines=2, placeholder='…')
        for j, content in enumerate(lines):
            body += text(30, y+24+j*17,content,11,'muted')
        body += text(30, y+66, 'PUSHED ' + repo['pushed'],9,'muted') + line(30,y+84,620,y+84)
        summaries.append(f'{repo["name"]} ({repo["primary"]}), pushed {repo["pushed"]}. {desc}')
        card = f'<g transform="translate(0,{-28-i*114})">{body[card_start:]}</g>'
        card += text(620,90,'OPEN REPOSITORY →',9,'muted','end')
        write_pair(out,f'work-{i+1}',repo['name'],summaries[-1],116,card)
    if not recent:
        body += text(0,55,'No public projects to show yet.',12,'muted')
    write_pair(out,'recent','Recent work',' '.join(summaries) or 'No public projects.',max(100, 34+114*len(recent)),body)

    for i, (name, title) in enumerate((('about','ABOUT'),('recent','RECENT WORK'),('stack','STACK'),('stats','STATS')),1):
        body = text(0,31,f'{i:02d}',10,'muted') + text(30,31,title,11) + line(50+len(title)*7,27,620,27)
        write_pair(out,'hd-'+name,title,title,58,body)
    body = text(310,26,'ETHAN B. CHEN',26,anchor='middle',extra='letter-spacing="3"') + text(310,53,'@'+data['login'],12,'muted','middle')
    body += text(310,78,'CODE / EXPERIMENTS / SYSTEMS',9,'muted','middle')
    write_pair(out,'identity','Ethan B. Chen','Ethan B. Chen, @'+data['login'],102,body)
    draw_atlas(repos,out)
    checkpoints = draw_milestones(days,repos,out)
    return description, streak_desc, lang_desc, recent, repos, draw_pulse(days,out), checkpoints, discovery(data,repository_description)


def update_readme(path, summary, streak, langs, recent, repos, pulse, checkpoints, discovery_html):
    content = path.read_text()
    language_list = '\n'.join('- '+item for item in langs.split('; '))
    recent_text = '\n\n'.join(f'**{r["name"]}** ({r["primary"]}), pushed {r["pushed"]}. {repository_description(r)}' for r in recent)
    links = '\n\n'.join(f'<a href="{esc(r["url"])}" title="Open {esc(r["name"])}">\n'+picture(f'work-{i+1}',f'{r["name"]}: {repository_description(r)} — open repository')+'\n</a>\n\n'+project_notes(r,repository_description(r)) for i,r in enumerate(recent))
    for name, replacement in (('discovery',discovery_html), ('comparison',comparison(repos)), ('recent-links', links), ('project-index',project_index(repos)), ('activity-text', f'{summary}\n\n{streak}\n\n{pulse}\n\n{checkpoints}\n\n**Languages**\n\n{language_list}\n\n**Recent work**\n\n{recent_text}')):
        pattern = rf'(<!-- {name}:start -->).*?(<!-- {name}:end -->)'
        content, count = re.subn(pattern, lambda m: m[1]+'\n'+replacement+'\n'+m[2], content, flags=re.S)
        if count != 1:
            raise ValueError(f'Expected one README marker pair: {name}')
    path.write_text(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--username', default=os.getenv('GH_LOGIN', os.getenv('GITHUB_REPOSITORY_OWNER', 'EthanChenHyland')))
    parser.add_argument('--as-of', type=date.fromisoformat, default=datetime.now(timezone.utc).date())
    parser.add_argument('--snapshot', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'generated')
    parser.add_argument('--readme', type=Path, default=ROOT/'README.md')
    args = parser.parse_args()
    if args.snapshot:
        data = json.loads(args.snapshot.read_text())
    else:
        token = os.getenv('GITHUB_TOKEN') or os.getenv('GH_TOKEN')
        if not token:
            parser.error('Set GITHUB_TOKEN, or use --snapshot generated/activity.json for offline rendering.')
        data = fetch(args.username, args.as_of, token)
    validate_data(data)
    summaries = render(data, args.output)
    update_readme(args.readme, *summaries)
    (args.output/'activity.json').write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')
    print(f'Generated profile for {data["login"]}: {sum(d["count"] for d in data["days"])} contributions, {len(data["repositories"])} repositories.')


if __name__ == '__main__':
    main()
