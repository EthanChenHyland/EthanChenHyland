"""Deterministic project atlas, rotating spotlight, and rolling milestones."""
from collections import Counter
from datetime import date
from svg import esc, line, rect, text, write_pair


def next_target(value, step):
    return (value // step + 1) * step


def spotlight(repos, as_of):
    candidates = sorted((r for r in repos if not r['archived']), key=lambda r: r['name'].casefold())
    return candidates[date.fromisoformat(as_of).toordinal() % len(candidates)] if candidates else None


def draw_atlas(repos, out):
    ordered = sorted(repos, key=lambda r: r['name'].casefold())
    totals = Counter()
    for repo in ordered:
        totals.update({k:v for k,v in repo['languages'].items() if v > 0})
    languages = sorted(totals, key=lambda k: (-totals[k], k))[:6]
    height = max(6,len(ordered)) * 42 + 103
    body = text(0,16,'PROJECT ATLAS',10,'muted') + text(620,16,'SHARED LANGUAGES',10,'muted','end')
    ys = {lang:62+i*42 for i,lang in enumerate(languages)}
    for i,repo in enumerate(ordered):
        y = 62+i*42
        for lang in languages:
            if repo['languages'].get(lang,0) > 0:
                body += f'<path d="M238 {y-4} C330 {y-4} 368 {ys[lang]-4} 460 {ys[lang]-4}" class="rule" stroke-width="1.2"/>'
        label = repo['name'] if len(repo['name']) <= 29 else repo['name'][:28]+'…'
        body += text(0,y,label,11) + rect(235,y-7,6,6)
    for lang,y in ys.items():
        body += rect(457,y-7,6,6) + text(478,y,lang,12)
    body += line(0,height-49,620,height-49)
    body += text(0,height-25,'Connections show presence, not proficiency or code volume.',10,'muted')
    body += text(0,height-7,'Six largest languages by bytes · full comparison below',9,'muted')
    if not ordered:
        body += text(0,62,'No public projects yet.',12,'muted')
    desc = 'Project language connections. '+ '; '.join(r['name']+': '+', '.join(k for k in languages if r['languages'].get(k,0)>0) for r in ordered)
    write_pair(out,'atlas','Project atlas',desc,height,body)
    return desc


def draw_milestones(days, repos, out):
    values = [(sum(d['count'] for d in days),100,'CONTRIBUTIONS'),
              (sum(d['count']>0 for d in days),25,'ACTIVE DAYS'),
              (len({k for r in repos for k,v in r['languages'].items() if v>0}),5,'LANGUAGES')]
    body = text(0,16,'NEXT CHECKPOINTS',10,'muted')
    descriptions=[]
    for i,(value,step,label) in enumerate(values):
        x=i*214
        target=next_target(value,step)
        body += text(x,55,value,30)+text(x,77,f'/ {target} {label}',9,'muted')
        body += rect(x,96,186,5,'soft')+rect(x,96,round(186*value/target,2),5)
        body += text(x,122,f'{target-value} to next checkpoint',9,'muted')
        descriptions.append(f'{label.lower()}: {value}, next checkpoint {target}')
    body += line(0,145,620,145)+text(0,166,'Activity: rolling 365 days · languages: current public code',9,'muted')
    desc='; '.join(descriptions)+'. Activity uses the rolling 365-day window; language count uses current public code. These are automatic numeric checkpoints, not GitHub awards.'
    write_pair(out,'milestones','Next checkpoints',desc,184,body)
    return desc


def comparison(repos):
    rows=[]
    for r in sorted(repos,key=lambda r:r['name'].casefold()):
        languages=' · '.join(k for k,v in sorted(r['languages'].items(),key=lambda item:(-item[1],item[0])) if v>0)
        status='Archived' if r['archived'] else 'Open'
        rows.append(f'<tr><td><a href="{esc(r["url"])}">{esc(r["name"])}</a></td><td>{esc(languages or "Unclassified")}</td><td>{esc(r["pushed"])}</td><td>{status}</td></tr>')
    return '<details>\n<summary><samp>COMPARE THE PROJECTS</samp></summary>\n<table>\n<tr><th>Project</th><th>Languages by code size</th><th>Last push · UTC</th><th>Status</th></tr>\n'+'\n'.join(rows)+'\n</table>\n</details>'


def discovery(data, describe):
    repo=spotlight(data['repositories'],data['as_of'])
    if not repo:
        return ''
    return ('<details>\n<summary><samp>THE FROG PICKED A PROJECT FOR YOU</samp></summary>\n'
            f'<p><b><a href="{esc(repo["url"])}">{esc(repo["name"])}</a></b></p>\n'
            f'<p>{esc(describe(repo))}</p>\n'
            f'<p><sub>A rotating daily spotlight · {esc(data["as_of"])} UTC</sub></p>\n</details>')
