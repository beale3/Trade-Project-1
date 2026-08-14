import pandas as pd, numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score, confusion_matrix
pd.set_option('display.width', 160)
np.seterr(all='ignore')

scan = pd.read_csv(r'C:\Users\beale\Downloads\scan_log.csv')
scan = scan[scan['nonstd_ticker_flag']==0].copy()
scan['scan_date'] = pd.to_datetime(scan['scan_date'])
scan['price'] = scan['open']
scan['dollar_vol_today'] = scan['price']*scan['volume']
scan['baseline_avg_vol'] = scan['volume']/scan['rel_vol']
scan['baseline_dollar_vol'] = scan['price']*scan['baseline_avg_vol']
scan['rel_vol_tail'] = scan['rel_vol'] > 50
scan['in_price_band'] = (scan['price']>=0.5)&(scan['price']<=20)
scan['core_pass'] = scan['in_price_band']&(scan['gain_pct']>=10)&(scan['rel_vol']>=2)&(scan['baseline_dollar_vol']>=250000)

def pband(p):
    if p < 2: return 'sub2'
    elif p <= 20: return 'core'
    else: return 'above20'
scan['bucket'] = scan['price'].apply(pband)

si = pd.read_csv(r'C:\Users\beale\short-interest-study\raw_short_interest_all.csv')
si['settlement_date'] = pd.to_datetime(si['settlement_date'])
si = si.sort_values('settlement_date')
scan_s = scan.sort_values('scan_date')
m = pd.merge_asof(scan_s, si.rename(columns={'settlement_date':'si_date'}),
                   left_on='scan_date', right_on='si_date', by='ticker', direction='backward',
                   tolerance=pd.Timedelta('45D'))
m['si_gate_state'] = np.where(m['days_to_cover'].isna(), 'unknown',
                       np.where(m['days_to_cover']>=3.0, 'pass', 'fail'))

def category(r):
    if not r['core_pass']:
        return 'FAIL'
    if r['rel_vol_tail']:
        return 'EXTREME_TAIL'
    if r['si_gate_state']=='pass':
        return 'FULL_PASS'
    if r['si_gate_state']=='fail':
        return 'CORE_SI_FAIL'
    return 'CORE_SI_UNKNOWN'
m['category'] = m.apply(category, axis=1)

print('='*110); print('SECTION 4 -- per-category forward-return backtest targets'); print('='*110)
for band in ('core','sub2'):
    print(f'\n--- price band: {band} ---')
    d = m[m['bucket']==band]
    for cat in ('FULL_PASS','CORE_SI_FAIL','CORE_SI_UNKNOWN','EXTREME_TAIL','FAIL'):
        g = d[d['category']==cat]
        if len(g)==0:
            print(f'  {cat:16s} n=0'); continue
        f1w = g['fwd_1w_ret'].dropna(); f1m = g['fwd_1m_ret'].dropna()
        print(f'  {cat:16s} n={len(g):5d}  '
              f'1D_mean={g["fwd_1d_ret"].mean():+.4f} 1W_mean={f1w.mean():+.4f} 1M_mean={f1m.mean():+.4f} '
              f'1M_median={f1m.median():+.4f} 1M_pos%={ (f1m>0).mean()*100:5.1f} '
              f'1M_p95={f1m.quantile(.95):+.3f} 1M_p99={f1m.quantile(.99):+.3f} '
              f'roundtrip%={(f1w<-0.20).mean()*100:5.1f} runner50%={(f1w>0.50).mean()*100:5.1f} runner100%={(f1w>1.0).mean()*100:5.1f}')

print(); print('='*110); print('naive baseline (whole scan_log population, each band)'); print('='*110)
for band in ('core','sub2'):
    d = m[m['bucket']==band]
    f1m = d['fwd_1m_ret'].dropna()
    print(f'  {band}: n={len(d)}  1M_mean={f1m.mean():+.4f} 1M_median={f1m.median():+.4f} 1M_pos%={(f1m>0).mean()*100:.1f}')

print(); print('='*110); print('BINARY MODELS vs naive: AUC / Spearman / confusion matrix, target = fwd_1m_ret>0'); print('='*110)
def eval_binary(df, flagcol, label, restrict=None):
    d = df.dropna(subset=['fwd_1m_ret', flagcol])
    if restrict is not None:
        d = d[restrict(d)]
    if len(d) < 10 or d[flagcol].nunique() < 2:
        print(f'  {label}: insufficient n or no variation (n={len(d)})'); return
    y = (d['fwd_1m_ret']>0).astype(int)
    x = d[flagcol].astype(int)
    try:
        auc = roc_auc_score(y, x)
    except Exception:
        auc = float('nan')
    rho, p = stats.spearmanr(x, d['fwd_1m_ret'])
    cm = confusion_matrix(y, x)
    lift = d[x==1]['fwd_1m_ret'].mean() - d[x==0]['fwd_1m_ret'].mean()
    print(f'  {label}: n={len(d)} pos_rate(flag=1)={ (d[x==1]["fwd_1m_ret"]>0).mean()*100 if (x==1).sum()>0 else float("nan"):.1f}% '
          f'vs flag=0 {(d[x==0]["fwd_1m_ret"]>0).mean()*100 if (x==0).sum()>0 else float("nan"):.1f}%  '
          f'AUC={auc:.3f} Spearman={rho:.3f} (p={p:.3f}) mean_return_lift={lift:+.4f}')
    print(f'      confusion matrix [rows=actual pos/neg, cols=pred 0/1]:\n{cm}')

def ease_of_entry_proxy(rel_vol, dtc):
    vscore = np.clip(rel_vol/5.0, 0, 1)*10
    if pd.isna(dtc):
        return vscore*0.7  # can't blend squeeze bonus without SI data -- partial proxy only
    sscore = np.clip(np.log1p(dtc)/np.log1p(10.0), 0, 1)*10
    return np.clip(0.7*vscore + 0.3*sscore, 0, 10)

m['si_pass_flag'] = (m['si_gate_state']=='pass').astype(int)
m['ease_proxy'] = m.apply(lambda r: ease_of_entry_proxy(r['rel_vol'], r['days_to_cover']), axis=1)
core_d = m[m['bucket']=='core']
sub2_d = m[m['bucket']=='sub2']

print('-- core $2-20 band --')
eval_binary(core_d, 'core_pass', 'core_pass_only')
eval_binary(core_d[core_d['si_gate_state']!='unknown'], 'si_pass_flag', 'si_gate_only (SI-matched subset)')
eval_binary(core_d, 'rel_vol_tail', 'rel_vol_tail_only (flag=1 means EXCLUDED/bad)')
eval_binary(core_d, 'core_pass', 'full_composite (core_pass AND NOT tail)', restrict=lambda d: ~d['rel_vol_tail'])

print('-- sub-2 band --')
eval_binary(sub2_d, 'core_pass', 'core_pass_only')
eval_binary(sub2_d[sub2_d['si_gate_state']!='unknown'], 'si_pass_flag', 'si_gate_only (SI-matched subset, n small)')
eval_binary(sub2_d, 'rel_vol_tail', 'rel_vol_tail_only')

print(); print('='*110); print('CONTINUOUS MODELS: LOO + 5-fold x 30-seed vs naive baseline (matches short-interest-study harness)'); print('='*110)

def run_continuous(df, feat_col, label, n_seeds=30, k=5):
    d = df.dropna(subset=[feat_col,'fwd_1m_ret']).copy()
    n = len(d)
    if n < 20:
        print(f'  {label}: n={n} too small, skipping'); return
    x = d[feat_col].values.astype(float); y = d['fwd_1m_ret'].values.astype(float)
    rho, p = stats.spearmanr(x, y)
    slope, intercept, r, p_lin, se = stats.linregress(x, y)
    ci = 1.96*se
    # LOO
    from numpy.polynomial import polynomial as P
    loo_err_model, loo_err_naive = [], []
    for i in range(n):
        mask = np.ones(n, dtype=bool); mask[i]=False
        sl, ic = np.polyfit(x[mask], y[mask], 1)
        pred = sl*x[i]+ic
        loo_err_model.append((pred-y[i])**2)
        loo_err_naive.append((y[mask].mean()-y[i])**2)
    loo_model_rmse = np.sqrt(np.mean(loo_err_model)); loo_naive_rmse = np.sqrt(np.mean(loo_err_naive))
    # 5-fold x 30 seed
    beats = 0
    for seed in range(n_seeds):
        rng = np.random.default_rng(seed)
        idx = rng.permutation(n)
        folds = np.array_split(idx, k)
        model_errs, naive_errs = [], []
        for f in folds:
            train = np.setdiff1d(idx, f)
            sl, ic = np.polyfit(x[train], y[train], 1)
            pred = sl*x[f]+ic
            model_errs.extend((pred-y[f])**2)
            naive_errs.extend((y[train].mean()-y[f])**2)
        if np.sqrt(np.mean(model_errs)) < np.sqrt(np.mean(naive_errs)):
            beats += 1
    seed_agree = beats/n_seeds*100
    print(f'  {label}: n={n}  Spearman rho={rho:.3f} p={p:.3f}  OLS slope={slope:.5f} (+/-{ci:.5f}, p={p_lin:.3f})')
    print(f'      LOO RMSE model={loo_model_rmse:.4f} vs naive={loo_naive_rmse:.4f}  (model {"beats" if loo_model_rmse<loo_naive_rmse else "does NOT beat"} naive)')
    print(f'      5-fold x {n_seeds}-seed: model beats naive baseline in {beats}/{n_seeds} seeds ({seed_agree:.1f}%)')
    return dict(label=label, n=n, rho=rho, p=p, slope=slope, p_lin=p_lin, seed_agree=seed_agree,
                loo_beats_naive=loo_model_rmse<loo_naive_rmse)

m['ease_proxy'] = m.apply(lambda r: ease_of_entry_proxy(r['rel_vol'], r['days_to_cover']), axis=1)

results = []
print('-- core $2-20 band --')
results.append(run_continuous(core_d, 'days_to_cover', 'days_to_cover (SI-matched subset)'))
results.append(run_continuous(core_d, 'ease_proxy', 'S3 ease-of-entry proxy (partial S3, all core-pass rows)'))
print('-- sub-2 band --')
results.append(run_continuous(sub2_d, 'days_to_cover', 'days_to_cover (SI-matched subset, n small)'))
results.append(run_continuous(sub2_d, 'ease_proxy', 'S3 ease-of-entry proxy'))

print(); print('='*110); print('ACCEPTANCE CRITERIA CHECK (core $2-20 band, days_to_cover model, per your Section 8)'); print('='*110)
r = [x for x in results if x and x['label']=='days_to_cover (SI-matched subset)']
if r:
    r = r[0]
    print(f"  slope>0 & p<0.05: {'PASS' if r['slope']>0 and r['p_lin']<0.05 else 'FAIL'} (slope={r['slope']:.5f}, p={r['p_lin']:.4f})")
    print(f"  Spearman>0.05: {'PASS' if r['rho']>0.05 else 'FAIL'} (rho={r['rho']:.3f})")
    print(f"  seed agreement >=90%: {'PASS' if r['seed_agree']>=90 else 'FAIL'} ({r['seed_agree']:.1f}%)")
    print(f"  LOO beats naive: {'PASS' if r['loo_beats_naive'] else 'FAIL'}")
