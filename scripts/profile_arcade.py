"""Repository-owned challenge boards and native README reveals."""
import json
from svg import ROOT, text, write_pair, esc
from field_guide import panel


def arcade(data, out):
    puzzles=json.loads((ROOT/'assets/demos/puzzles.json').read_text())
    challenges=[]
    for number,puzzle in enumerate(puzzles,1):
        body=text(310,27,f'CHALLENGE {number:02d} / WHITE TO MOVE',13,anchor='middle')
        positions=[]
        for row,encoded in enumerate(puzzle['fen'].split()[0].split('/')):
            cells=[]
            for p in encoded: cells.extend(['']*int(p) if p.isdigit() else [p])
            for col,p in enumerate(cells):
                x,y=150+40*col,50+40*row
                body+=f'<rect x="{x}" y="{y}" width="40" height="40" fill="{["#d2ddbf","#718c65"][(row+col)%2]}"/>'
                if p:
                    positions.append(f'{dict(K="White king",Q="White queen",k="Black king")[p]} on {"abcdefgh"[col]}{8-row}')
                    glyph={'K':'♔','Q':'♕','k':'♚'}[p]
                    body+=f'<text x="{x+20}" y="{y+31}" text-anchor="middle" style="font-family:Georgia,serif;font-size:35px;fill:#102619">{glyph}</text>'
            body+=text(138,76+row*40,8-row,11,'muted','end')
        for col,c in enumerate('abcdefgh'):body+=text(170+40*col,390,c,11,'muted','middle')
        alt='; '.join(positions)+'. Find mate in one.'
        name=f'challenge-{number}'
        write_pair(out,name,f'Chess challenge {number}',alt,410,body)
        picture=f'<picture><source media="(prefers-color-scheme: dark)" srcset="generated/{name}-dark.svg"><img src="generated/{name}.svg" width="620" alt="{esc(alt)}"></picture>'
        m=puzzle['solutions'][0]
        hint=panel('SHOW A HINT',f'<p>Look for a queen move to the {m["uci"][2]}-file.</p>')
        answer=panel('CHECK YOUR ANSWER',f'<p><b>{esc(m["san"])}</b> — queen from {m["uci"][:2]} to {m["uci"][2:]}. The king is checked and has no legal reply.</p>')
        challenges.append(panel(f'CHALLENGE {number:02d}',picture+'\n'+hint+'\n'+answer))
    sets=[panel(f'PUZZLES {start+1:02d}–{min(start+4,len(challenges)):02d}', '\n'.join(challenges[start:start+4])) for start in range(0,len(challenges),4)]
    archive=panel(f'THE CHESS CORNER · {len(challenges)} CHALLENGES','<p>Fixed practice positions from the verified puzzle collection, grouped in sets of four. White to move, mate in one. Open a board, solve it, then check your answer. Each position has exactly one mating move.</p>\n'+'\n'.join(sets))
    commits=sorted((r for r in data['repositories'] if r.get('latest_commit')),key=lambda r:(r['latest_commit']['date'],r['name']),reverse=True)
    rows=''.join(f'<tr><td>{esc(r["latest_commit"]["date"])}</td><td>{esc(r["name"])}</td><td>{esc(r["latest_commit"]["headline"])}</td></tr>' for r in commits)
    log=panel('THE BUILD LOG · LATEST CHANGE IN EACH PROJECT', '<p>An automatically refreshed snapshot of each project’s latest default-branch commit, newest dates first.</p><table><tr><th>UTC date</th><th>Project</th><th>Latest change</th></tr>'+rows+'</table>' if commits else '<p>No default-branch commits in this snapshot.</p>')
    questions=[('01 · DOES A HIGH MUSIC MATCH SCORE MEAN GREAT PLAYING?', 'No. This example measures agreement with a known score on synthesized audio. It does not grade a human performance.'),('02 · DOES MORE CODE IN A LANGUAGE MEAN MORE EXPERTISE?', 'No. The language charts measure bytes in public repositories. They describe the codebase, not proficiency.'),('03 · DOES SEARCHING MORE CHESS POSITIONS GUARANTEE A BETTER MOVE?', 'No. Search depth, evaluation quality, move ordering, and the position itself all matter. A node count alone does not measure move quality.')]
    quiz=panel('THREE THINGS THE DEMOS DO NOT TELL YOU', '<p>Make a prediction before opening each answer.</p>'+'\n'.join(panel(q,'<p>'+a+'</p>') for q,a in questions))
    return '\n'.join([archive,log,quiz])
