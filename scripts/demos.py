"""Looping visual replays of captured project runs; no fabricated telemetry."""
import csv,json
from svg import ROOT,esc,text,rect,write_pair


def draw_demos(out):
    chess=json.loads((ROOT/'assets/demos/chess.json').read_text())
    frames=[{'fen':chess['initial'],'san':'START','search':{'depth':0,'nodes':0}}]+chess['moves']
    body=text(0,16,'FUN CHESS ENGINE / RECORDED SELF-PLAY',10,'muted');rules=''
    for row in range(8):
        for col in range(8):body+=rect(24+col*28,42+row*28,28,28,'soft', 'style="fill:'+('#607a54' if (row+col)%2 else '#b3c49d')+'"')
    glyphs=dict(zip('KQRBNPkqrbnp','♔♕♖♗♘♙♚♛♜♝♞♟'))
    for i,frame in enumerate(frames):
        a=i/len(frames)*100;b=(i+1)/len(frames)*100
        rules+=f'@keyframes f{i}{{0%{{opacity:{1 if i==0 else 0}}}{a:.4f}%{{opacity:1}}{b:.4f}%,100%{{opacity:0}}}}'
        piece=''
        for row,r in enumerate(frame['fen'].split()[0].split('/')):
            chars=''.join(' '*int(c) if c.isdigit() else glyphs[c] for c in r)
            xs=' '.join(str(38+n*28) for n in range(8))
            piece+=text(xs,64+row*28,chars,25,'ink','middle','xml:space="preserve" style="font-family:Georgia,serif;fill:#10231b"')
        piece+=text(290,80,frame['san'],29)+text(290,118,f'PLY {i:02d} / {len(frames)-1}',10,'muted')
        piece+=text(290,156,f'DEPTH {frame["search"]["depth"]}',12)+text(290,181,f'{frame["search"]["nodes"]:,} nodes',12,'muted')
        body+=f'<g class="demo-frame frame-{i}" style="opacity:{1 if i==0 else 0};animation:f{i} {len(frames)*.9}s steps(1,end) infinite">{piece}</g>'
    body+=text(290,227,'180 ms / move budget',10,'muted')+text(290,249,'Actual engine output',10,'muted')
    rules+='@media(prefers-reduced-motion:reduce){.demo-frame{animation:none!important;opacity:0!important}.frame-0{opacity:1!important}}'
    write_pair(out,'demo-chess','FunChessEngine in motion','Recorded self-play: 24 legal moves selected by FunChessEngine, with actual search telemetry. Source commit '+chess['commit'],288,body,'<style>'+rules+'</style>')
    rows=list(csv.DictReader((ROOT/'assets/demos/piano-chroma.csv').read_text().splitlines()))
    labels=['C','Cs','D','Ds','E','F','Fs','G','Gs','A','As','B']
    body=text(0,16,'PIANO MIR / SCORE MEETS SOUND',10,'muted')
    # Sample the real chroma output into 80 time columns, preserving recorded values.
    for col in range(80):
        r=rows[round(col*(len(rows)-1)/79)]
        for n,label in enumerate(labels):
            value=float(r['audio_'+label]);body+=rect(38+col*6.8,49+(11-n)*12,6,10,'ink',f'opacity="{max(.06,value):.3f}"')
    for n,label in enumerate(labels):body+=text(0,58+(11-n)*12,label.replace('s','#'),9,'muted')
    body+='<path d="M38 42V196" class="stroke piano-scan" stroke-width="1.5"/>'
    meta=json.loads((ROOT/'assets/demos/piano.json').read_text());score=meta['final_result']['headline_score']
    body+=text(0,226,f'{score:.2f} / 100',21)+text(220,226,'SAME-SOURCE VERIFICATION',10,'muted')
    body+=text(0,254,'Real Rust analysis · synthetic Minuet excerpt · 12 seconds',10,'muted')
    rules='@keyframes pianoScan{to{transform:translateX(537px)}}.piano-scan{animation:pianoScan 12s linear infinite}@media(prefers-reduced-motion:reduce){.piano-scan{animation:none}}'
    write_pair(out,'demo-piano','Piano MIR analysis replay',f'Actual detected pitch-class evidence from a synthetic Minuet excerpt. Same-source verification score {score:.2f}; this is score-informed verification, not blind transcription or a human performance grade.',278,body,'<style>'+rules+'</style>')
