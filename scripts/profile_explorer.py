"""Native language browsing, monthly activity, and a branching frog story."""
from collections import defaultdict
from datetime import date
from field_guide import panel
from svg import esc


def monthly_activity(days):
    months=defaultdict(list)
    for day in days:
        months[day['date'][:7]].append(day)
    sections=[]
    for month,entries in sorted(months.items(),reverse=True):
        total=sum(d['count'] for d in entries)
        active=[d for d in entries if d['count']>0]
        label=date.fromisoformat(month+'-01').strftime('%B %Y').upper()
        rows=''.join(f'<tr><td>{esc(d["date"])}</td><td>{d["count"]}</td></tr>' for d in sorted(active,key=lambda d:(-d['count'],d['date']))[:3])
        detail='<table><tr><th>Most active dates</th><th>Contributions</th></tr>'+rows+'</table>' if active else '<p>No contributions recorded in this part of the calendar.</p>'
        sections.append(panel(f'{label} · {total} CONTRIBUTIONS',f'<p>{len(active)} active days across {len(entries)} days in the snapshot.</p>{detail}<p><sub>Coverage: {entries[0]["date"]} through {entries[-1]["date"]} UTC.</sub></p>'))
    return panel('THE YEAR, MONTH BY MONTH','<p>Open a month to see its activity and three busiest dates. Boundary months cover only the dates included in the rolling 365-day snapshot; today may be incomplete.</p>\n'+'\n'.join(sections))


def language_browser(repos):
    languages=defaultdict(list)
    for repo in repos:
        for language,size in repo['languages'].items():
            if size>0: languages[language].append(repo)
    sections=[]
    for language,matches in sorted(languages.items()):
        rows=[]
        for repo in sorted(matches,key=lambda r:r['name'].casefold()):
            languages_bytes=sum(v for v in repo['languages'].values() if v>0)
            share=100*repo['languages'][language]/languages_bytes
            rows.append(f'<tr><td>{esc(repo["name"])}</td><td>{share:.1f}%</td><td>{esc(repo["pushed"])}</td></tr>')
        sections.append(panel(f'{language.upper()} · {len(matches)} PROJECT'+('S' if len(matches)!=1 else ''),'<table><tr><th>Project</th><th>Share of language bytes</th><th>Latest push · UTC</th></tr>'+''.join(rows)+'</table>'))
    return panel('FIND PROJECTS BY LANGUAGE','<p>Choose a language to see every matching public project. Percentages describe that language’s share of each repository’s detected language bytes.</p>\n'+'\n'.join(sections))


def frog_story():
    reeds=panel('FOLLOW THE FIREFLIES','<p>The lights blink in pairs. Beneath the reeds, a tiny frog is trying to debug the moon’s reflection.</p>'+panel('OFFER A RUBBER DUCK','<p>“It only breaks when I look at it,” says the frog. The duck says nothing. The frog solves it anyway.</p><p><b>Ending: honorary pond debugger.</b> 🦆</p>')+panel('WAIT QUIETLY','<p>The water settles. The moon becomes round again. Some bugs are ripples.</p><p><b>Ending: a moment of peace.</b> 🌙</p>'))
    stone=panel('INVESTIGATE THE CHECKERED STONE','<p>A beetle guards a tiny chessboard. “One move,” it says. “Then you may pass.”</p>'+panel('CHALLENGE THE BEETLE','<p>The beetle pushes a pawn sideways. You politely explain the rules. It insists this is a variant.</p><p><b>Ending: undefeated by technicality.</b> ♟</p>')+panel('ASK FOR DIRECTIONS','<p>The beetle points toward the Chess Corner above. “Those positions have actually been checked.”</p><p><b>Ending: a sensible detour.</b> 🐸</p>'))
    return panel('A TINY FROG ADVENTURE','<p>You arrive at the pond at dusk. A path forks between glowing reeds and a checkered stone. Open a choice, then choose again.</p>'+reeds+stone+'<p><sub>A little fictional detour. Close the choices to start again; nothing is saved.</sub></p>')


def explorer(data):
    return '\n'.join([frog_story(),language_browser(data['repositories']),monthly_activity(data['days'])])
