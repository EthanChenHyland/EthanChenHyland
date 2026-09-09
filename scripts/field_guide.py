"""Expandable, self-contained profile features with no browser runtime."""
from svg import ROOT, esc
import json


def panel(title, body):
    return f'<details>\n<summary><samp>{esc(title)}</samp></summary>\n{body}\n</details>'


def field_guide(data):
    routes = [
        ('I LIKE GAMES & SEARCH', 'FunChessEngine', 'Follow a position from legal moves to search to evaluation. The recorded self-play demo below shows the engine choosing for both sides.'),
        ('I LIKE MUSIC & SIGNALS', 'PianoMirRustPublic', 'Follow audio through pitch evidence and alignment with a known score. Open the lab results below to see what the captured example actually measured.'),
        ('I LIKE DATA & AUTOMATION', 'kitcoscraper', 'Explore the path from a web source to extracted data. The project notes show its latest public change.'),
        ('I LIKE AI EXPERIMENTS', 'the-great-prompt-off', 'Explore a project organized around comparing prompts. The project browser below contains its current languages and latest public activity.'),
    ]
    repos = {r['name']:r for r in data['repositories']}
    cards=[]
    for title, name, why in routes:
        if name not in repos: continue
        r=repos[name]
        languages=' · '.join(k for k,v in sorted(r['languages'].items(),key=lambda x:(-x[1],x[0])) if v>0)
        cards.append(panel(title, f'<p><b>{esc(name)}</b></p><p>{esc(why)}</p><p><sub>{esc(languages)} · latest push {esc(r["pushed"])}</sub></p>'))
    chooser=panel('CHOOSE YOUR PATH', '<p>Pick an interest to find a starting point in my work.</p>\n'+'\n'.join(cards))
    p=json.loads((ROOT/'assets/demos/piano.json').read_text())
    values=[('Score-aligned verification',f'{p["final_result"]["verification_score"]:.2f} / 100','Overall evidence that this audio matches its known score.'),('Note score',f'{p["note_score"]:.2f}','Note matching component of this captured run.'),('Timing score',f'{p["timing_score"]:.2f}','Timing alignment component.'),('Chroma score',f'{p["chroma_score"]:.2f}','Pitch-class evidence component.'),('Missing notes',str(p['missing_notes']),'Missing notes reported by this run.')]
    table='<table><tr><th>Measurement</th><th>Result</th><th>Meaning</th></tr>'+''.join('<tr>'+''.join(f'<td>{esc(c)}</td>' for c in row)+'</tr>' for row in values)+'</table>'
    lab=panel('OPEN THE MUSIC ANALYSIS LAB',f'<p>One captured experiment: a 12-second synthesized Minuet excerpt compared with its source score.</p>{table}'+panel('WHAT DOES 94.78 ACTUALLY MEAN?', '<p>The system was given the score. It checks whether the audio agrees with that score. These component scores are separate measurements, not percentages to add together.</p><p>This result does not measure a pianist’s skill or prove that the system can transcribe unfamiliar music. The input is synthesized, with no human performance.</p>'))
    days=data['days']; recent=days[-7:]; previous=days[-14:-7]
    current=sum(d['count'] for d in recent); old=sum(d['count'] for d in previous)
    delta=current-old
    peak=max(recent,key=lambda d:d['count'])
    strongest=f'{peak["date"]} ({peak["count"]} contributions)' if peak['count'] else 'No contributions in this window'
    week=panel('THIS WEEK IN NUMBERS',f'<p><b>{current} contributions</b> across {sum(d["count"]>0 for d in recent)} active days.</p><p>{delta:+d} contributions compared with the preceding seven days ({old}).</p><p>Busiest day: {strongest}.</p><p><sub>{recent[0]["date"]} through {recent[-1]["date"]} UTC. The current day may be incomplete. Activity counts describe frequency, not code quality.</sub></p>')
    return '<a name="field-guide"></a>\n<p><samp>THE FIELD GUIDE · OPEN SOMETHING THAT INTERESTS YOU</samp></p>\n'+chooser+'\n'+lab+'\n'+week
