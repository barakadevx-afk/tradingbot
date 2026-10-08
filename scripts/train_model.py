\"\"\"Train AI models for BARAKA AI.\"\"\"
import sys
sys.path.insert(0, '.')

import numpy as np
import pandas as pd
from ml_engine.features.feature_engineering import FeatureEngineer
from ml_engine.training.trainer import ModelTrainer
from ml_engine.registry.model_registry import ModelRegistry


def generate_training_data(n_samples=5000):
    np.random.seed(42)
    data = {
        'returns': np.random.randn(n_samples) * 0.02,
        'volume_change': np.random.randn(n_samples) * 0.3,
        'rsi': np.random.uniform(20, 80, n_samples),
        'macd_hist': np.random.randn(n_samples) * 0.001,
        'atr_pct': np.random.uniform(0.01, 0.05, n_samples),
        'ema_distance': np.random.randn(n_samples) * 0.02,
        'bb_position': np.random.uniform(0, 1, n_samples),
        'trend_strength': np.random.uniform(0, 100, n_samples),
        'volatility': np.random.uniform(0.01, 0.08, n_samples),
    }
    df = pd.DataFrame(data)
    df['target'] = np.where(df['returns'].shift(-1) > 0, 1, 0)
    df = df.dropna()
    return df


def train_model():
    print('Generating training data...')
    data = generate_training_data()

    print('Engineering features...')
    engineer = FeatureEngineer()
    features = engineer.transform(data)

    print('Training model...')
    trainer = ModelTrainer()
    result = trainer.train(
        data=features,
        target_col='target',
        model_type='xgboost',
        strategy='trend_following'
    )

    print(f'Training complete.')
    print(f'  Model: {result["model_info"]["name"]}')
    print(f'  Version: {result["model_info"]["version"]}')
    print(f'  Accuracy: {result["metrics"]["accuracy"]:.4f}')
    print(f'  F1 Score: {result["metrics"]["f1_score"]:.4f}')
    print(f'  AUC: {result["metrics"]["auc"]:.4f}')

    return result


if __name__ == '__main__':
    train_model()
