import numpy as np, wave, struct
SR=44100; TOTAL=38.0; BPM=96; beat=60/BPM
N=int(SR*TOTAL); t=np.arange(N)/SR
out=np.zeros(N)
rng=np.random.default_rng(7)
def add(sig,start):
    i=int(start*SR); n=min(len(sig),N-i)
    if n>0: out[i:i+n]+=sig[:n]
def env(n,a,d,level=1.0):
    e=np.ones(n)*level; ra=int(a*SR); rd=int(d*SR)
    if ra>0: e[:ra]*=np.linspace(0,1,ra)
    if rd>0 and rd<n: e[-rd:]*=np.linspace(1,0,rd)
    return e
def kick(dur=.35):
    n=int(dur*SR); tt=np.arange(n)/SR
    f=np.exp(-tt*28)*120+45
    return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt*9)*0.9
def hat(dur=.06,level=.18):
    n=int(dur*SR); x=rng.standard_normal(n)
    x=np.diff(x,prepend=0)  # brighten
    return x*np.exp(-np.arange(n)/SR*90)*level
def snare(dur=.2):
    n=int(dur*SR); tt=np.arange(n)/SR
    x=rng.standard_normal(n)*np.exp(-tt*22)*0.35+np.sin(2*np.pi*190*tt)*np.exp(-tt*30)*0.4
    return x
def bass(freq,dur):
    n=int(dur*SR); tt=np.arange(n)/SR
    x=np.sign(np.sin(2*np.pi*freq*tt))*0.5+np.sin(2*np.pi*freq*tt)*0.5
    # simple lowpass via moving average
    k=int(SR/(freq*6)); x=np.convolve(x,np.ones(k)/k,mode='same')
    return x*env(n,.01,.08,0.32)
def pad(freqs,dur,level=.09):
    n=int(dur*SR); tt=np.arange(n)/SR; x=np.zeros(n)
    for f in freqs:
        for det in (-0.4,0,0.4):
            x+=np.sin(2*np.pi*(f+det)*tt+rng.uniform(0,6))
    x/= (len(freqs)*3)
    return x*env(n,.6,.6,level)*(0.85+0.15*np.sin(2*np.pi*0.7*tt))
def whoosh(dur=.45,level=.5,rise=True):
    n=int(dur*SR); tt=np.arange(n)/SR; x=rng.standard_normal(n)
    # bandpass-ish sweep by modulating a resonant filter crudely: mix of filtered noise
    k=np.linspace(60,6,n) if rise else np.linspace(6,60,n)
    y=np.zeros(n); acc=0.0
    for i in range(n):
        a=1.0/k[i]; acc+=a*(x[i]-acc); y[i]=x[i]-acc
    e=np.sin(np.pi*tt/dur)**1.5
    return y*e*level
def hit(level=.8):
    n=int(.8*SR); tt=np.arange(n)/SR
    x=np.sin(2*np.pi*(55*np.exp(-tt*3)+40)*tt)*np.exp(-tt*4)+rng.standard_normal(n)*np.exp(-tt*18)*0.4
    return x*level
def pluck(freq,dur=.25,level=.12):
    n=int(dur*SR); tt=np.arange(n)/SR
    x=np.sin(2*np.pi*freq*tt)+0.3*np.sin(2*np.pi*freq*2*tt)
    return x*np.exp(-tt*10)*level

# chord progression (Am - F - C - G) lo-fi, 2 bars each
chords=[(220,261.6,329.6),(174.6,220,261.6),(130.8*2,164.8*2,196*2),(196,246.9,293.7)]
roots=[55,43.65,65.4,49]
bar=beat*4
MUSIC_START=2.4
b=0; tcur=MUSIC_START
while tcur<TOTAL:
    ci=(b//2)%4
    add(pad(chords[ci],bar*1.02),tcur)
    for step in range(16):
        ts=tcur+step*beat/4
        if step%4==0: add(kick(),ts)
        if step in (4,12): add(snare(),ts)
        if step%2==0: add(hat(level=.16 if step%4 else .22),ts+ (0.012 if step%4==2 else 0))
        if step in (0,3,6,10,11,14): add(bass(roots[ci]*(2 if step in (6,14) else 1),beat/4*1.6),ts)
        if step in (2,7,13) and b%2==1: add(pluck(chords[ci][(step*7)%3]*2),ts)
    tcur+=bar; b+=1

# SFX synced to scenes
scenes=[0.0,2.6,7.2,11.0,14.8,18.6,22.4,25.6,30.4,34.0]
add(whoosh(1.4,.35,True),0.15)          # riser under the hook
add(hit(.9),1.5)                           # "Plus maintenant." slam
for s in scenes[1:]: add(whoosh(.4,.4,False),s-0.12)
# word ticks in hook
for tt_ in (0.05,0.35,0.65): add(pluck(880,.12,.08),tt_)
# CTA shimmer
for i,f in enumerate((523,659,784,1047)): add(pluck(f,.5,.12),34.4+i*.09)
# arpège scintillant sur la séquence 3D
for i in range(12): add(pluck((523,659,784,1047,1319)[i%5]*(1 if i<8 else 2),.35,.06),25.9+i*.22)
# fade out last 1.2s + fade in
out*=env(N,0.05,1.2)
out/=np.max(np.abs(out))*1.05
w=wave.open('music.wav','wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((out*32767).astype('<i2').tobytes()); w.close(); print('ok')
