"""Static chapters from an actual recorded chess game, readable in GitHub."""
import json
from field_guide import panel
from svg import ROOT, text, rect, esc, write_pair


def replay_book(out):
    recording=json.loads((ROOT/'assets/demos/chess.json').read_text())
    moves=recording['moves'];chapters=[]
    glyphs=dict(zip('KQRBNPkqrbnp','♔♕♖♗♘♙♚♛♜♝♞♟'))
    for start in range(0,len(moves),4):
        end=min(start+4,len(moves));frame=moves[end-1];name=f'replay-page-{start//4+1}'
        body=text(310,22,f'AFTER {end} HALF-MOVES / {frame["san"]}',12,anchor='middle')
        for row,encoded in enumerate(frame['fen'].split()[0].split('/')):
            col=0
            for c in encoded:
                for p in (' '*int(c) if c.isdigit() else c):
                    x,y=150+col*40,45+row*40
                    body+=rect(x,y,40,40,'soft','style="fill:'+('#718c65' if (row+col)%2 else '#d2ddbf')+'"')
                    square='abcdefgh'[col]+str(8-row)
                    if square==frame['uci'][2:]:body+=f'<rect x="{x+2}" y="{y+2}" width="36" height="36" fill="none" stroke="#eaff77" stroke-width="3"/>'
                    if p!=' ':body+=text(x+20,y+31,glyphs[p],35,'ink','middle','style="font-family:Georgia,serif;fill:#102619"')
                    col+=1
            body+=text(137,71+row*40,8-row,11,'muted','end')
        for col,c in enumerate('abcdefgh'):body+=text(170+col*40,387,c,11,'muted','middle')
        desc=f'Recorded board after {end} half-moves. Last move {frame["san"]}, from {frame["uci"][:2]} to {frame["uci"][2:]}.'
        write_pair(out,name,'Chess replay chapter '+str(start//4+1),desc,404,body)
        rows=[]
        for i in range(start,end):
            m=moves[i];s=m['search']
            detail=f'{s["nodes"]:,} nodes · depth {s["depth"]}' if s['nodes'] else 'No search recorded'
            rows.append(f'<tr><td>{i//2+1}{". White" if i%2==0 else "… Black"}</td><td>{esc(m["san"])}</td><td>{detail}</td></tr>')
        picture=f'<picture><source media="(prefers-color-scheme: dark)" srcset="generated/{name}-dark.svg"><img src="generated/{name}.svg" width="620" alt="{esc(desc)}"></picture>'
        chapters.append(panel(f'CHAPTER {start//4+1} · MOVES {start//2+1}–{(end+1)//2}',picture+'<table><tr><th>Turn</th><th>Played</th><th>Recorded search</th></tr>'+''.join(rows)+'</table>'))
    glossary=panel('HOW TO READ THE REPLAY','<p>Each chapter covers two full turns. The diagram shows the position at the end of that chapter; the highlighted square is the last move’s destination.</p><p>N = knight, B = bishop, R = rook, Q = queen, K = king. A move without a piece letter is a pawn move; x means capture, + means check, and # means checkmate.</p><p>A half-move is one player’s turn. Nodes count positions searched; depth is the reported search depth. Zero nodes means no search was recorded for that move.</p>')
    return panel('THE REPLAY BOOK · A CHESS GAME IN SIX CHAPTERS','<p>Read the captured FunChessEngine self-play at your own pace. Open chapters in order, or compare boards by leaving multiple chapters expanded. This is a 24-half-move excerpt, not a completed game.</p>'+glossary+'\n'+'\n'.join(chapters)+f'<p><sub>Recorded source revision: {esc(recording["commit"][:12])}.</sub></p>')


def logic_corner():
    pads=panel('01 · HOW MANY WAYS ACROSS THE POND?', '<p>A frog starts on pad 0 and wants to reach pad 4. It can hop forward by one or two pads. How many distinct sequences of hops reach pad 4 exactly?</p>'+panel('REVEAL THE REASONING','<p><b>Five:</b> 1+1+1+1, 1+1+2, 1+2+1, 2+1+1, and 2+2.</p><p>Every route ends with a one-pad or two-pad hop, so ways(n) = ways(n−1) + ways(n−2). Start with ways(0) = 1 and ways(1) = 1.</p>'))
    bits=panel('02 · THE FIREFLY MESSAGE','<p>Three fireflies can each be on or off. How many distinct patterns can they display, including all off?</p>'+panel('REVEAL THE REASONING','<p><b>Eight.</b> Each light doubles the possibilities: 2 × 2 × 2. In binary: 000, 001, 010, 011, 100, 101, 110, 111.</p><p>Add one more firefly and there are 16 patterns.</p>'))
    search=panel('03 · FIND THE HEAVIER PEBBLE','<p>Eight pebbles look identical. Exactly one is heavier. With a balance scale, can you always find it in two weighings?</p>'+panel('REVEAL THE REASONING','<p><b>Yes.</b> Weigh three against three. If they balance, weigh the two remaining pebbles against each other. Otherwise, take the heavier group of three and weigh one against another: the heavier one wins, or a balance identifies the third.</p><p>The three possible outcomes of a balance comparison let you narrow the candidates faster than a yes/no question.</p>'))
    return panel('THE LOGIC LILY PAD · THREE SMALL BRAINTEASERS','<p>Think through a puzzle, then open its explanation.</p>'+pads+bits+search)
