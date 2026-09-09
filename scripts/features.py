"""Native README interactions and compact recent-activity graphics."""
from urllib.parse import quote
from svg import esc, line, text, write_pair


def activity_windows(days):
    return {
        'week': sum(d['count'] for d in days[-7:]),
        'previous_week': sum(d['count'] for d in days[-14:-7]),
        'month': sum(d['count'] for d in days[-30:]),
        'active_month': sum(d['count'] > 0 for d in days[-30:]),
    }


def draw_pulse(days, out):
    values = activity_windows(days)
    delta = values['week'] - values['previous_week']
    body = text(0,16,'RECENT ACTIVITY',10,'muted')
    for x,label,value in ((0,'LAST 7 DAYS',values['week']), (218,'LAST 30 DAYS',values['month']), (446,'ACTIVE / 30 DAYS',values['active_month'])):
        body += text(x,56,value,30) + text(x,79,label,10,'muted')
    body += line(0,96,620,96)
    body += text(0,119,f'{delta:+d} contributions vs previous 7 days',10,'muted')
    body += text(620,119,'INCLUDING TODAY · UTC',9,'muted','end')
    description = (f'Last 7 UTC days: {values["week"]} contributions; previous 7 days: {values["previous_week"]}; '
                   f'last 30 days: {values["month"]} contributions over {values["active_month"]} active days. Includes today, which is unfinished.')
    write_pair(out,'pulse','Recent activity',description,138,body)
    return description


def project_notes(repo, description):
    url = repo['url']
    branch = quote(repo.get('branch') or 'HEAD',safe='')
    languages = sorted(repo['languages'], key=lambda name: (-repo['languages'][name],name))
    links = [('Code',url),('Commits',url+'/commits/'+branch),('Releases',url+'/releases')]
    if repo.get('issues_enabled',False):
        links.append(('Issues',url+'/issues'))
    body = f'<p>{esc(description)}</p>'
    body += '<p><b>Languages:</b> '+esc(' · '.join(languages) or 'Not classified')+'</p>'
    commit = repo.get('latest_commit')
    if commit:
        body += f'<p><b>Latest default-branch commit:</b><br><a href="{esc(commit["url"])}">{esc(commit["headline"])}</a><br><sub>{esc(commit["date"])} UTC</sub></p>'
    release = repo.get('release')
    if release:
        body += f'<p><b>Latest release:</b> <a href="{esc(release["url"])}">{esc(release["tag"])}</a> · {esc(release["date"])}</p>'
    body += '<p><samp>'+' · '.join(f'<a href="{esc(target)}">{label}</a>' for label,target in links)+'</samp></p>'
    return f'<details>\n<summary><samp>EXPLORE {esc(repo["name"])}</samp></summary>\n<div align="left">\n{body}\n</div>\n</details>'


def project_index(repos):
    items = []
    for repo in sorted(repos,key=lambda r:(r['primary'].casefold(),r['name'].casefold())):
        archive = ' · archived' if repo['archived'] else ''
        items.append(f'<li><a href="{esc(repo["url"])}">{esc(repo["name"])}</a> — {esc(repo["primary"])}{archive}</li>')
    return (f'<details>\n<summary><samp>BROWSE ALL {len(repos)} PROJECTS</samp></summary>\n'
            '<div align="left">\n<p>Public, non-fork projects, grouped by primary language.</p>\n<ul>\n'
            +'\n'.join(items)+'\n</ul>\n</div>\n</details>')
