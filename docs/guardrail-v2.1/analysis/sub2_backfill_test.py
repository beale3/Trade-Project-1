import pandas as pd, numpy as np
from scipy import stats
from sklearn.metrics import roc_auc_score, confusion_matrix
pd.set_option('display.width', 160)

d = pd.read_csv(r'C:\Users\beale\AppData\Local\Temp\claude\C--Users-beale-Software-Dev\aaabd589-8a92-4e09-adb0-dc578804b16e\scratchpad\guardrail_conditioned_sub2.csv')
print('n =', len(d))
print('date range:', d['date'].min(), '->', d['date'].max())
print('unique tickers:', d['ticker'].nunique())

def run_continuous(df, feat_col, target_col, label, n_seeds=30, k=5):
    dd = df.dropna(subset=[feat_col, target_col]).copy()
    n = len(dd)
    x = dd[feat_col].values.astype(float); y = dd[target_col].values.astype(float)
    rho, p = stats.spearmanr(x, y)
    pear_r, pear_p = stats.pearsonr(x, y)
    slope, intercept, r, p_lin, se = stats.linregress(x, y)
    ci = 1.96*se
    loo_err_model, loo_err_naive = [], []
    for i in range(n):
        mask = np.ones(n, dtype=bool); mask[i]=False
        sl, ic = np.polyfit(x[mask], y[mask], 1)
        pred = sl*x[i]+ic
        loo_err_model.append((pred-y[i])**2)
        loo_err_naive.append((y[mask].mean()-y[i])**2)
    loo_model_rmse = np.sqrt(np.mean(loo_err_model)); loo_naive_rmse = np.sqrt(np.mean(loo_err_naive))
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
    print(f'\n{label}: n={n}')
    print(f'  Pearson r={pear_r:.3f} (p={pear_p:.4f})   Spearman rho={rho:.3f} (p={p:.4f})')
    print(f'  OLS slope={slope:.5f} (+/-{ci:.5f}), p={p_lin:.4f}')
    print(f'  LOO RMSE: model={loo_model_rmse:.4f} vs naive={loo_naive_rmse:.4f}  --> model {"BEATS" if loo_model_rmse<loo_naive_rmse else "DOES NOT BEAT"} naive')
    print(f'  5-fold x {n_seeds}-seed: model beats naive in {beats}/{n_seeds} seeds ({seed_agree:.1f}%)')
    return dict(n=n, rho=rho, p=p, slope=slope, p_lin=p_lin, seed_agree=seed_agree, loo_beats=loo_model_rmse<loo_naive_rmse)

print('\n' + '='*100)
print('DAYS_TO_COVER vs forward returns, n=241 Guardrail-conditioned sub-$2 (historical backfill 2024-2026)')
print('='*100)
r1w = run_continuous(d, 'days_to_cover', 'fwd_1w_ret', 'days_to_cover -> fwd_1w_ret')
r1m = run_continuous(d, 'days_to_cover', 'fwd_1m_ret', 'days_to_cover -> fwd_1m_ret')

print('\n' + '='*100)
print('SI-GATE BINARY (pass/fail) vs positive-1M-return, AUC/confusion matrix')
print('='*100)
dd = d.dropna(subset=['fwd_1m_ret']).copy()
dd['si_pass'] = (dd['si_gate_state']=='pass').astype(int)
y = (dd['fwd_1m_ret']>0).astype(int)
x = dd['si_pass']
auc = roc_auc_score(y, x)
rho, p = stats.spearmanr(x, dd['fwd_1m_ret'])
cm = confusion_matrix(y, x)
lift = dd[x==1]['fwd_1m_ret'].mean() - dd[x==0]['fwd_1m_ret'].mean()
pos_pass = (dd[x==1]['fwd_1m_ret']>0).mean()*100
pos_fail = (dd[x==0]['fwd_1m_ret']>0).mean()*100
print(f'n={len(dd)} (pass={x.sum()}, fail={(1-x).sum()})')
print(f'pos-rate: pass={pos_pass:.1f}% vs fail={pos_fail:.1f}%   AUC={auc:.3f}  Spearman={rho:.3f} (p={p:.3f})  mean-return-lift={lift:+.4f}')
print('confusion matrix [rows=actual pos/neg, cols=pred fail/pass]:')
print(cm)

print('\n' + '='*100)
print('REL-VOL TAIL vs forward returns (within this conditioned n=241)')
print('='*100)
tail = dd[dd['rel_vol_tail']==1]['fwd_1m_ret']
notail = dd[dd['rel_vol_tail']==0]['fwd_1m_ret']
print(f'tail (n={len(tail)}): mean={tail.mean():+.4f} median={tail.median():+.4f} pos%={ (tail>0).mean()*100:.1f}')
print(f'not-tail (n={len(notail)}): mean={notail.mean():+.4f} median={notail.median():+.4f} pos%={ (notail>0).mean()*100:.1f}')
w = dd.dropna(subset=['fwd_1w_ret'])
rt_tail = (w[w['rel_vol_tail']==1]['fwd_1w_ret']<-0.20).mean()*100
rt_notail = (w[w['rel_vol_tail']==0]['fwd_1w_ret']<-0.20).mean()*100
print(f'round-trip rate: tail={rt_tail:.1f}%  not-tail={rt_notail:.1f}%')

print('\n' + '='*100)
print('ACCEPTANCE CRITERIA CHECK (Section 8, applied to this n=241 SI-gate continuous model, fwd_1m)')
print('='*100)
print(f"  slope>0 & p<0.05: {'PASS' if r1m['slope']>0 and r1m['p_lin']<0.05 else 'FAIL'} (slope={r1m['slope']:.5f}, p={r1m['p_lin']:.4f})")
print(f"  Spearman>0.05: {'PASS' if r1m['rho']>0.05 else 'FAIL'} (rho={r1m['rho']:.3f})")
print(f"  seed agreement >=90%: {'PASS' if r1m['seed_agree']>=90 else 'FAIL'} ({r1m['seed_agree']:.1f}%)")
print(f"  LOO beats naive: {'PASS' if r1m['loo_beats'] else 'FAIL'}")
print(f"  AUC>0.55 (binary si-gate model): {'PASS' if auc>0.55 else 'FAIL'} (AUC={auc:.3f})")
