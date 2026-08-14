import pandas as pd, numpy as np
from scipy import stats
pd.set_option('display.width', 160)

scan = pd.read_csv(r'C:\Users\beale\Downloads\scan_log.csv')
scan = scan[scan['nonstd_ticker_flag']==0].copy()
scan['scan_date'] = pd.to_datetime(scan['scan_date'])
scan['price'] = scan['open']
scan['dollar_vol_today'] = scan['price']*scan['volume']
scan['baseline_avg_vol'] = scan['volume']/scan['rel_vol']            # reconstruct avg_vol_20d
scan['baseline_dollar_vol'] = scan['price']*scan['baseline_avg_vol']  # "typical" liquidity, pre-spike

def bucket(p):
    if p < 2: return 'sub2'
    elif p <= 20: return 'core'
    else: return 'above20'
scan['bucket'] = scan['price'].apply(bucket)

sub2 = scan[scan['bucket']=='sub2'].copy()
core = scan[scan['bucket']=='core'].copy()

print('='*100); print('1A. Denominator-effect false positives within sub-$2 core-passes'); print('='*100)
s2_pass = sub2[(sub2['gain_pct']>=10)&(sub2['rel_vol']>=2)].copy()
for cut in (25000, 50000, 100000, 250000):
    frac = (s2_pass['baseline_dollar_vol'] < cut).mean()*100
    print(f'  share of sub-2 core-passes with baseline (pre-spike) $-volume < ${cut:,}: {frac:.1f}%  (n={ (s2_pass["baseline_dollar_vol"]<cut).sum() } of {len(s2_pass)})')
thin = s2_pass[s2_pass['baseline_dollar_vol']<50000]
robust = s2_pass[s2_pass['baseline_dollar_vol']>=50000]
print(f'  thin-baseline (<$50k) group: n={len(thin)}, mean rel_vol={thin["rel_vol"].mean():.1f}, fwd_1d mean={thin["fwd_1d_ret"].mean():.4f}, fwd_1w<-20% rate={ (thin["fwd_1w_ret"]<-0.20).mean()*100:.1f}%')
print(f'  robust-baseline (>=$50k) group: n={len(robust)}, mean rel_vol={robust["rel_vol"].mean():.1f}, fwd_1d mean={robust["fwd_1d_ret"].mean():.4f}, fwd_1w<-20% rate={ (robust["fwd_1w_ret"]<-0.20).mean()*100:.1f}%')

print(); print('='*100); print('1B / 5A. Dollar-volume vs rel-vol tail; where does a dv floor bite?'); print('='*100)
valid = sub2.replace([np.inf,-np.inf], np.nan).dropna(subset=['baseline_dollar_vol','rel_vol'])
lr = stats.pearsonr(np.log10(valid['baseline_dollar_vol']+1), np.log10(valid['rel_vol']+1))
print(f'  corr(log baseline $-vol, log rel_vol) in sub-2: r={lr[0]:.3f}, p={lr[1]:.2e}, n={len(valid)}')
print('  round-trip rate (fwd_1w<-20%) by baseline $-volume quintile, sub-2:')
q = sub2.dropna(subset=['fwd_1w_ret','baseline_dollar_vol']).copy()
q['dvq'] = pd.qcut(q['baseline_dollar_vol'], 5, labels=['Q1_thinnest','Q2','Q3','Q4','Q5_deepest'])
print(q.groupby('dvq', observed=True)['fwd_1w_ret'].apply(lambda s: f"{(s<-0.20).mean()*100:.1f}% (n={len(s)})"))
print('  candidates remaining if filtering sub-2 by today $-dollar-volume >= X:')
for X in (250_000, 500_000, 1_000_000, 2_000_000):
    n = (sub2['dollar_vol_today']>=X).sum()
    print(f'    >= ${X:,}: {n} of {len(sub2)} sub-2 candidates remain ({n/len(sub2)*100:.1f}%)')

print(); print('='*100); print('2A. Simulate rel_vol>=3x for sub-$2 (core-pass + SI-gate + fwd returns)'); print('='*100)
si = pd.read_csv(r'C:\Users\beale\short-interest-study\raw_short_interest_all.csv')
si['settlement_date'] = pd.to_datetime(si['settlement_date'])
si = si.sort_values('settlement_date')
scan_s = scan.sort_values('scan_date')
merged = pd.merge_asof(scan_s, si.rename(columns={'settlement_date':'si_date'}),
                        left_on='scan_date', right_on='si_date', by='ticker', direction='backward',
                        tolerance=pd.Timedelta('45D'))
m_sub2 = merged[merged['bucket']=='sub2'].copy()

for thr in (2,3):
    cp = sub2[(sub2['gain_pct']>=10)&(sub2['rel_vol']>=thr)]
    hassi = m_sub2[(m_sub2['gain_pct']>=10)&(m_sub2['rel_vol']>=thr)&m_sub2['days_to_cover'].notna()]
    sigate = hassi[hassi['days_to_cover']>=3.0]
    print(f'  rel_vol>={thr}: core-pass n={len(cp)} ({len(cp)/124:.2f}/day), of those w/ SI data n={len(hassi)}, SI-gate pass n={len(sigate)}')
    print(f'      core-pass fwd_1d mean={cp["fwd_1d_ret"].mean():.4f} median={cp["fwd_1d_ret"].median():.4f}, fwd_1w mean={cp["fwd_1w_ret"].mean():.4f}, fwd_1w<-20% rate={(cp["fwd_1w_ret"]<-0.20).mean()*100:.1f}%')

print(); print('='*100); print('2B. Rel-vol confidence cap (>50x) — does excluding it change the return profile?'); print('='*100)
capped = sub2[sub2['rel_vol']<=50]
uncapped_tail = sub2[sub2['rel_vol']>50]
for name,g in (('rel_vol<=50 (capped)',capped), ('rel_vol>50 (excluded tail)',uncapped_tail)):
    print(f'  {name}: n={len(g)}, fwd_1d mean={g["fwd_1d_ret"].mean():.4f} std={g["fwd_1d_ret"].std():.4f}, fwd_1w mean={g["fwd_1w_ret"].mean():.4f} std={g["fwd_1w_ret"].std():.4f}, fwd_1w<-20%={(g["fwd_1w_ret"]<-0.20).mean()*100:.1f}%, fwd_1w>+50%={(g["fwd_1w_ret"]>0.50).mean()*100:.1f}%')

print(); print('='*100); print('3A. Predictive slope of days_to_cover vs forward returns, by price band'); print('='*100)
for name, g in (('sub2', m_sub2), ('core', merged[merged['bucket']=='core'])):
    d = g.dropna(subset=['days_to_cover','fwd_1w_ret'])
    if len(d) > 5:
        r1w = stats.pearsonr(d['days_to_cover'], d['fwd_1w_ret'])
        slope1w = np.polyfit(d['days_to_cover'], d['fwd_1w_ret'], 1)[0]
        d2 = g.dropna(subset=['days_to_cover','fwd_1m_ret'])
        r1m = stats.pearsonr(d2['days_to_cover'], d2['fwd_1m_ret'])
        slope1m = np.polyfit(d2['days_to_cover'], d2['fwd_1m_ret'], 1)[0]
        print(f'  {name} (n_1w={len(d)}, n_1m={len(d2)}): fwd_1w r={r1w[0]:.3f} p={r1w[1]:.3f} slope={slope1w:.5f}  |  fwd_1m r={r1m[0]:.3f} p={r1m[1]:.3f} slope={slope1m:.5f}')

print(); print('='*100); print('3B. SI-gate threshold sensitivity for sub-2 (n small - flag noise)'); print('='*100)
for thr in (2.5, 3.0, 3.5):
    g = m_sub2[(m_sub2['days_to_cover']>=thr)]
    print(f'  thr={thr}: n={len(g)}, fwd_1w mean={g["fwd_1w_ret"].mean():.4f} median={g["fwd_1w_ret"].median():.4f}, fwd_1m mean={g["fwd_1m_ret"].mean():.4f}')

print(); print('='*100); print('4A. Round-trip attribution (logistic on rel_vol, baseline $-vol) in sub-2'); print('='*100)
from sklearn.linear_model import LogisticRegression
d = sub2.dropna(subset=['fwd_1w_ret','rel_vol','baseline_dollar_vol']).replace([np.inf,-np.inf],np.nan).dropna(subset=['baseline_dollar_vol'])
d['round_trip'] = (d['fwd_1w_ret']<-0.20).astype(int)
X = np.column_stack([np.log10(d['rel_vol']+1), np.log10(d['baseline_dollar_vol']+1)])
y = d['round_trip'].values
clf = LogisticRegression().fit(X,y)
print(f'  n={len(d)}, round_trip base rate={y.mean()*100:.1f}%')
print(f'  coef on log10(rel_vol): {clf.coef_[0][0]:.3f}   coef on log10(baseline $-vol): {clf.coef_[0][1]:.3f}')
print('  (positive coef on rel_vol = higher rel_vol raises round-trip odds; negative coef on $-vol = deeper liquidity lowers round-trip odds)')

print(); print('='*100); print('4B. P(outsized runner | SI-gate fail, sub-2)'); print('='*100)
gatefail = m_sub2[(m_sub2['days_to_cover'].notna())&(m_sub2['days_to_cover']<3.0)&(m_sub2['gain_pct']>=10)&(m_sub2['rel_vol']>=2)]
gatepass = m_sub2[(m_sub2['days_to_cover'].notna())&(m_sub2['days_to_cover']>=3.0)&(m_sub2['gain_pct']>=10)&(m_sub2['rel_vol']>=2)]
for name,g in (('SI-gate FAIL',gatefail), ('SI-gate PASS',gatepass)):
    gg = g.dropna(subset=['fwd_1w_ret'])
    print(f'  {name}: n={len(gg)}, P(fwd_1w>+50%)={(gg["fwd_1w_ret"]>0.50).mean()*100:.1f}%, P(fwd_1w>+100%)={(gg["fwd_1w_ret"]>1.0).mean()*100:.1f}%')

print(); print('='*100); print('6B. Settlement-cycle sample-size projection for sub-2 SI n'); print('='*100)
ndays = scan['scan_date'].nunique()
sub2_si_n = m_sub2['days_to_cover'].notna().sum()
rate_per_day = sub2_si_n/ndays
print(f'  sub-2 candidates with matched SI data: {sub2_si_n} over {ndays} trading days = {rate_per_day:.3f}/day')
for target in (150, 250, 400):
    add_days = (target-sub2_si_n)/rate_per_day
    add_cycles = add_days/261*26  # approx trading days/year -> ~26 biweekly settlement cycles/yr
    print(f'  to reach n={target}: need ~{add_days:.0f} more trading days (~{add_days/21:.1f} months, ~{add_cycles:.1f} more settlement cycles)')
