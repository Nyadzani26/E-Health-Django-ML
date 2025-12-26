import pandas as pd
from django.core.management.base import BaseCommand
from sklearn.model_selection import train_test_split
from sklearn import linear_model
from sklearn.metrics import r2_score
import os

class Command(BaseCommand):
    help = 'Trains the diabetes prediction model from CSV data'

    def handle(self, *args, **options):
        self.stdout.write('Starting model training...')
        
        # Load dataset
        # We assume the CSV is in data_model/diabetes_data.csv relative to the project root
        csv_path = "data_model/diabetes_data.csv"
        if not os.path.exists(csv_path):
            self.stdout.write(self.style.ERROR(f'CSV file not found at {csv_path}'))
            return

        df = pd.read_csv(csv_path)

        X = df[["age", "sex", "bmi", "bp", "tc",
                "ldl", "hdl", "tch", "ltg", "glucose"]]
        Y = df['Result']

        x_train, x_test, y_train, y_test = train_test_split(
            X, Y, test_size=0.3, random_state=1)

        model = linear_model.LinearRegression()
        model.fit(x_train, y_train)

        # Evaluate
        test_preds = model.predict(x_test)
        score = r2_score(y_test, test_preds)
        self.stdout.write(self.style.SUCCESS(f'Model trained. R2 Score: {score:.4f}'))

        # Pickle model
        pickle_path = "data_model/model.pickle"
        pd.to_pickle(model, pickle_path)
        self.stdout.write(self.style.SUCCESS(f'Model saved to {pickle_path}'))
