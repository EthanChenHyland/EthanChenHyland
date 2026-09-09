"""Inspectable snapshots from the repository's captured chroma analysis."""
import csv
from field_guide import panel
from svg import ROOT, text, rect, write_pair, esc

PITCHES=('C','Cs','D','Ds','E','F','Fs','G','Gs','A','As','B')


def sample_frame(rows, seconds):
    return min(rows,key=lambda r:abs(float(r['time_seconds'])-seconds))


def strongest(row):
    values={p:float(row['audio_'+p]) for p in PITCHES}
    peak=max(values.values())
    return [p.replace('s','#') for p in PITCHES if values[p]==peak] if peak>0 else []


def microscope(out):
    rows=list(csv.DictReader((ROOT/'assets/demos/piano-chroma.csv').read_text().splitlines()))
    pages=[]
    for number,seconds in enumerate((0,3,6,9),1):
        row=sample_frame(rows,seconds);stamp=float(row['time_seconds']);name=f'sound-frame-{number}'
        body=text(310,25,f'SOUND MICROSCOPE / {stamp:.2f} SECONDS',13,anchor='middle')
        body+=text(155,58,'KNOWN SCORE',10,'muted','middle')+text(450,58,'DETECTED AUDIO',10,'muted','middle')
        for i,pitch in enumerate(PITCHES):
            y=80+i*24
            body+=text(26,y+12,pitch.replace('s','#'),11,'muted')
            for x,prefix in ((72,'score_'),(367,'audio_')):
                value=float(row[prefix+pitch])
                body+=rect(x,y,200,13,'soft')+rect(x,y,round(200*max(0,min(1,value)),3),13)
        body+=text(310,391,'Bar length = normalized pitch-class evidence (0 to 1)',10,'muted','middle')
        desc=f'Known-score and detected-audio pitch-class evidence at {stamp:.2f} seconds, from the captured synthesized Minuet analysis.'
        write_pair(out,name,'Sound microscope snapshot',desc,414,body)
        picture=f'<picture><source media="(prefers-color-scheme: dark)" srcset="generated/{name}-dark.svg"><img src="generated/{name}.svg" width="620" alt="{esc(desc)}"></picture>'
        peaks=strongest(row)
        answer=(', '.join(peaks)+' has the strongest recorded evidence.' if len(peaks)==1 else ', '.join(peaks)+' tie for strongest evidence.') if peaks else 'No positive pitch-class evidence was recorded in this frame.'
        answer=panel('REVEAL THE STRONGEST PITCH CLASS',f'<p><b>{esc(answer)}</b></p><p>This is a pitch class, not a single note or octave. Several notes can share a pitch class, and harmonics can also contribute evidence.</p>')
        values=''.join(f'<tr><td>{p.replace("s","#")}</td><td>{float(row["score_"+p]):.3f}</td><td>{float(row["audio_"+p]):.3f}</td></tr>' for p in PITCHES)
        raw=panel('INSPECT THE NUMBERS','<table><tr><th>Pitch class</th><th>Score evidence</th><th>Audio evidence</th></tr>'+values+'</table>')
        pages.append(panel(f'SNAPSHOT {number} · {stamp:.2f} SECONDS','<p>Which pitch class has the longest bar on the audio side? How closely does its pattern resemble the known score?</p>'+picture+answer+raw))
    guide=panel('WHAT AM I LOOKING AT?', '<p>Chroma groups pitches into the twelve pitch classes, ignoring octave. The left column comes from the known score; the right comes from analysis of the synthesized audio.</p><p>Longer bars mean stronger normalized evidence within that representation. They are not probabilities, loudness readings, or performance grades. The score and audio columns use their respective recorded normalizations.</p><p>These four frames are sampled near 0, 3, 6, and 9 seconds. They are individual snapshots, not averages across each three-second interval.</p>')
    return panel('THE SOUND MICROSCOPE · SCORE VS AUDIO','<p>Zoom into four moments of the captured Minuet analysis. Compare patterns, make a prediction, then reveal the answer or inspect all twelve values.</p>'+guide+'\n'+'\n'.join(pages))
