"""A contribution-eating ASCII frog, driven by the same validated UTC calendar."""
import base64
from pathlib import Path
from datetime import date
from svg import ROOT, text, rect, write_pair


def habitat(days):
    active=sum(d['count']>0 for d in days[-30:])
    week=sum(d['count'] for d in days[-7:])
    return min(12,(active+1)//2),min(20,(week+4)//5)


def draw_pond(days,out):
    start=date.fromisoformat(days[0]['date'])
    offset=(start.weekday()+1)%7
    positions=[(22+((i+offset)//7)*11,76+((i+offset)%7)*19) for i in range(len(days))]
    active=[i for i,d in enumerate(days) if d['count']>0]
    pads,flies=habitat(days)
    body=text(0,16,'THE CONTRIBUTION POND',10,'muted')+text(620,16,'A FROG WITH AN APPETITE',9,'muted','end')
    rules='';duration=max(8,len(active)*.9+2)
    for i,(d,(x,y)) in enumerate(zip(days,positions)):
        klass='ink' if d['count'] else 'rule'
        opacity='';anim=''
        if i in active:
            at=(active.index(i)+1)/(len(active)+2)*100
            name=f'eat{i}';opacity=f' style="animation:{name} {duration}s linear infinite"'
            rules+=f'@keyframes {name}{{0%,{max(0,at-.1):.3f}%{{opacity:1}}{at:.3f}%,94%{{opacity:.15}}100%{{opacity:1}}}}'
        body+=f'<circle cx="{x}" cy="{y}" r="{min(4,1.8+d["count"]*.12) if d["count"] else 1}" class="{klass} food"{opacity}/>'
    for p in range(pads):
        body+=f'<ellipse cx="{25+(p*101)%570}" cy="{224+p%2*8}" rx="13" ry="3" class="soft"/>'
    for f in range(flies):
        body+=f'<circle cx="{35+(f*137)%550}" cy="{44+(f*47)%160}" r="1" class="ink firefly" style="animation:twinkle {3+f%3}s ease-in-out {f*.2}s infinite"/>'
    frog=base64.b64encode((ROOT/'assets/demos/frog.svg').read_bytes()).decode()
    sequence=[(0,positions[active[0]] if active else (40,130))]+[((j+1)/(len(active)+2)*100,positions[i]) for j,i in enumerate(active)]
    keys=''
    for j,(at,(x,y)) in enumerate(sequence):
        keys+=f'{at:.3f}%{{transform:translate({x-31}px,{y-22}px)}}'
        if j+1<len(sequence):
            nxt,npos=sequence[j+1];keys+=f'{(at+nxt)/2:.3f}%{{transform:translate({(x+npos[0])/2-31:.1f}px,{(y+npos[1])/2-38:.1f}px)}}'
    x,y=sequence[-1][1];keys+=f'94%,100%{{transform:translate({x-31}px,{y-22}px)}}'
    body+=f'<g class="pond-frog" style="animation:hop {duration}s linear infinite"><image width="62" height="34" href="data:image/svg+xml;base64,{frog}"/></g>'
    body+=text(0,264,f'{pads} lily pads / {flies} fireflies',10,'muted')+text(620,264,'PLAY THE POND →',10,'muted','end')
    body+=text(0,286,'Pads: active days / 30 · fireflies: contributions / 7',9,'muted')
    rules+='@keyframes hop{'+keys+'}@keyframes twinkle{0%,100%{opacity:.15}50%{opacity:.8}}@media(prefers-reduced-motion:reduce){.food,.pond-frog,.firefly{animation:none!important}.pond-frog{transform:translate(260px,190px)}}'
    write_pair(out,'pond','The contribution pond',f'A frog hops through {len(active)} active days in the last 365 UTC days. {pads} lily pads reflect active days in the last month; {flies} fireflies reflect the last week. Animation changes only the picture, never GitHub activity.',306,body,'<style>'+rules+'</style>')

    light=base64.b64encode((ROOT/'assets/demos/frog-light.svg').read_bytes()).decode()
    target=Path(out)/'pond.svg'
    target.write_text(target.read_text().replace(frog,light))
