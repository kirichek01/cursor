"""train_ai_confidence.py

Обучает LightGBM‑модель для AI‑Confidence бота.
Финальная версия, которая корректно обрабатывает экспорт из MT5 с разделителем-табуляцией.
Использование:
    python train_ai_confidence.py --csv xauusd_m15.csv --out models/xau_m15_lgb.txt
"""
import argparse, pandas as pd, numpy as np, lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score

FEATS = ['rsi','ema_slope','atr','fibo_z','bos_dist','ob_width','vol_z','weekday','hour']

def feature_engineering(df):
    df['rsi'] = 50 + np.arctan((df.close - df.open)*10)*20/np.pi
    df['ema20'] = df.close.ewm(span=20, adjust=False).mean()
    df['ema_slope'] = df.ema20.pct_change()*10000
    df['atr'] = (df[['high','low','close']].max(axis=1)-df[['high','low','close']].min(axis=1)).rolling(14).mean()
    df['fibo_z'] = (df.close - df.low.rolling(50).min())/(df.high.rolling(50).max()-df.low.rolling(50).min()+1e-6)
    df['bos_dist'] = (df.close - df.close.shift(20)).abs()
    df['ob_width'] = (df.high - df.low).rolling(3).max()
    df['vol_z'] = (df.volume - df.volume.rolling(48).mean())/df.volume.rolling(48).std()
    df['weekday'] = df.index.weekday
    df['hour'] = df.index.hour
    # target: hit TP within 10 свч
    look = 10
    tp_hit = (df.close.shift(-look) - df.close) > df.atr.shift(-look)
    df['target'] = tp_hit.astype(int)
    return df.dropna()

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', required=True)
    ap.add_argument('--out', default='models/xau_m15_lgb.txt')
    args = ap.parse_args()

    # --- ФИНАЛЬНАЯ ЛОГИКА ЗАГРУЗКИ ---
    try:
        # Указываем правильный разделитель - табуляцию
        df = pd.read_csv(args.csv, sep='\t')
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        exit()

    # Очищаем имена колонок от скобок < > и приводим к нижнему регистру
    df.columns = [str(col).replace('<', '').replace('>', '').lower() for col in df.columns]

    # Собираем timestamp из отдельных колонок date и time
    if 'date' in df.columns and 'time' in df.columns:
        df['timestamp'] = pd.to_datetime(df['date'] + ' ' + df['time'])
    else:
        # Эта ошибка больше не должна появляться
        raise ValueError("Could not find 'date' and 'time' columns after parsing. Please check the CSV file.")
    
    # Переименовываем колонку с объемом
    if 'tickvol' in df.columns:
        df = df.rename(columns={'tickvol': 'volume'})
    
    if 'volume' not in df.columns:
        print("Warning: 'volume' column not found. Creating dummy column.")
        df['volume'] = 0

    df.set_index('timestamp', inplace=True)
    # --- КОНЕЦ ЛОГИКИ ЗАГРУЗКИ ---

    print("Data loaded successfully. Starting feature engineering...")
    df = feature_engineering(df)
    print("Feature engineering complete. Starting model training...")

    X = df[FEATS]; y = df['target']
    X_train,X_test,y_train,y_test = train_test_split(X,y,test_size=0.2,shuffle=False)
    
    model = lgb.LGBMClassifier(max_depth=4, n_estimators=200, learning_rate=0.05)
    model.fit(X_train,y_train)
    
    print(f"\nTraining complete. AUC score: {roc_auc_score(y_test, model.predict_proba(X_test)[:,1]):.4f}")
    model.booster_.save_model(args.out)
    print(f"Model saved to '{args.out}'")