"""Native README interactions, regenerated with the daily snapshot."""
import json
from datetime import date
from svg import ROOT, text, write_pair, esc
from field_guide import field_guide
from profile_arcade import arcade
from profile_explorer import explorer
from replay_book import replay_book, logic_corner
from sound_microscope import microscope


def extras(data, out):
    puzzles = json.loads((ROOT/'assets/demos/puzzles.json').read_text())
    day = data['days'][-1]['date']
    puzzle = puzzles[date.fromisoformat(day).toordinal() % len(puzzles)]
    body = text(310,24,'DAILY CHESS PUZZLE',14,anchor='middle')
    body += text(310,48,'White to move · mate in one',12,'muted','middle')
    names = {'K':'White king','Q':'White queen','k':'Black king'}
    glyphs = {'K':'♔','Q':'♕','k':'♚'}
    position=[]
    for row, encoded in enumerate(puzzle['fen'].split()[0].split('/')):
        squares=[]
        for p in encoded:
            squares.extend(['']*int(p) if p.isdigit() else [p])
        for col,p in enumerate(squares):
            x,y=150+col*40,70+row*40
            body += f'<rect x="{x}" y="{y}" width="40" height="40" fill="{["#d2ddbf","#718c65"][(row+col)%2]}"/>'
            if p:
                position.append(f'{names[p]} on {"abcdefgh"[col]}{8-row}')
                body += f'<text x="{x+20}" y="{y+31}" text-anchor="middle" style="font-family:Georgia,serif;font-size:35px;fill:#102619">{glyphs[p]}</text>'
        body += text(138,96+row*40,8-row,11,'muted','end')
    for i,c in enumerate('abcdefgh'): body += text(170+i*40,409,c,11,'muted','middle')
    body += text(310,437,day+' UTC · generated practice position',10,'muted','middle')
    description = '; '.join(position)+'. White to move, mate in one.'
    write_pair(out,'puzzle','Daily chess puzzle',description,453,body)
    solution=puzzle['solutions'][0]
    move=solution['uci']
    rows=''.join(f'<tr><td>{d["date"]}</td><td>{d["count"]}</td></tr>' for d in reversed(data['days'][-7:]))
    total=sum(d['count'] for d in data['days'][-7:])
    return f'''<a name="puzzle"></a>
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="generated/puzzle-dark.svg">
  <img src="generated/puzzle.svg" width="620" alt="{esc(description)}">
</picture>
<details>
<summary><samp>NEED A HINT?</samp></summary>
<p>The queen delivers mate on rank <b>{move[3]}</b>. Look for a square that checks the king and removes its escape squares.</p>
</details>
<details>
<summary><samp>REVEAL THE MOVE</samp></summary>
<p><b>{esc(solution['san'])}</b> — move the queen from <b>{move[:2]}</b> to <b>{move[2:]}</b>. The black king is in check with no legal escape.</p>
<p><sub>One of 16 verified practice positions, rotating daily. # means checkmate.</sub></p>
</details>
<a name="more-fun-stuff"></a>
<details>
<summary><samp>MORE FUN STUFF</samp></summary>

<details>
<summary><samp>OPEN THE 7-DAY ACTIVITY DIARY · {total} CONTRIBUTIONS</samp></summary>
<table><thead><tr><th>Date (UTC)</th><th>Contributions</th></tr></thead><tbody>{rows}</tbody></table>
<p><sub>GitHub contribution-calendar counts, updated with the profile. The current UTC day may be incomplete.</sub></p>
</details>
{field_guide(data)}
{arcade(data,out)}
{explorer(data)}
{replay_book(out)}
{logic_corner()}
{microscope(out)}
</details>'''
