import pandas as pd
import numpy as np
from fpdf import FPDF
import os
import random

CSV_DIR = "data/raw_csv"
PDF_DIR = "data/raw_pdf"
os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(PDF_DIR, exist_ok=True)

def generate_csvs():
    print("Generating CSV datasets...")
    # Movies
    movies = pd.DataFrame({
        'movie_id': range(1, 101),
        'title': [f"Movie {i}" for i in range(1, 101)],
        'genre': random.choices(['Action', 'Comedy', 'Drama', 'Sci-Fi', 'Horror'], k=100),
        'release_year': [random.randint(2020, 2025) for _ in range(100)],
        'budget': [random.randint(10, 200) * 1000000 for _ in range(100)],
        'revenue': [random.randint(5, 500) * 1000000 for _ in range(100)]
    })
    movies.loc[10, 'title'] = "Stellar Run" # For specific testing
    movies.to_csv(f"{CSV_DIR}/movies.csv", index=False)

    # Viewers
    viewers = pd.DataFrame({
        'viewer_id': range(1, 501),
        'name': [f"Viewer {i}" for i in range(1, 501)],
        'age': [random.randint(18, 70) for _ in range(500)],
        'country': random.choices(['USA', 'UK', 'India', 'Canada', 'Germany'], k=500),
        'subscription_type': random.choices(['Basic', 'Standard', 'Premium'], k=500)
    })
    viewers.to_csv(f"{CSV_DIR}/viewers.csv", index=False)

    # Watch Activity
    activity = pd.DataFrame({
        'activity_id': range(1, 1001),
        'viewer_id': [random.randint(1, 500) for _ in range(1000)],
        'movie_id': [random.randint(1, 100) for _ in range(1000)],
        'watch_date': pd.date_range(start='2024-01-01', periods=1000, freq='h').strftime('%Y-%m-%d %H:%M:%S'),
        'duration_minutes': [random.randint(10, 180) for _ in range(1000)]
    })
    activity.to_csv(f"{CSV_DIR}/watch_activity.csv", index=False)

    # Reviews
    reviews = pd.DataFrame({
        'review_id': range(1, 301),
        'movie_id': [random.randint(1, 100) for _ in range(300)],
        'rating': [random.randint(1, 10) for _ in range(300)],
        'comment': [f"Great movie {i}" if i % 2 == 0 else f"Could be better {i}" for i in range(300)]
    })
    reviews.to_csv(f"{CSV_DIR}/reviews.csv", index=False)

    # Marketing Spend
    marketing = pd.DataFrame({
        'campaign_id': range(1, 51),
        'movie_id': [random.randint(1, 100) for _ in range(50)],
        'spend': [random.randint(50000, 1000000) for _ in range(50)],
        'channel': random.choices(['Social Media', 'TV', 'Billboard', 'Email'], k=50)
    })
    marketing.to_csv(f"{CSV_DIR}/marketing_spend.csv", index=False)

    # Regional Performance
    regional = pd.DataFrame({
        'region_id': range(1, 21),
        'region_name': [f"Region {i}" for i in range(1, 21)],
        'total_revenue': [random.randint(100, 1000) * 100000 for _ in range(20)],
        'active_users': [random.randint(1000, 50000) for _ in range(20)]
    })
    regional.to_csv(f"{CSV_DIR}/regional_performance.csv", index=False)

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Internal Business Report - Confidential', 0, 1, 'C')
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)
    def chapter_body(self, body):
        self.set_font('Arial', '', 11)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdfs():
    print("Generating PDF reports...")
    reports = [
        ("Quarterly Executive Report", "This report outlines Q1 2025 results. Revenue up 15%. Stellar Run is performing exceptionally well in European markets."),
        ("Campaign Performance Summary", "Marketing campaigns for 'Last Kingdom' on Social Media show 40% higher ROI than TV."),
        ("Content Roadmap", "2025 focus: Sci-Fi and Thrillers. Comedy market is currently weak and saturated."),
        ("Policy Guidelines", "All internal queries must be routed through the AI Assistant. Data security is paramount."),
        ("Audience Behavior Report", "Younger audiences (18-24) prefer shorter engagement periods and binge-watching.")
    ]
    for title, body in reports:
        pdf = PDFReport()
        pdf.add_page()
        pdf.chapter_title(title)
        pdf.chapter_body(body)
        filename = title.lower().replace(" ", "_") + ".pdf"
        pdf.output(f"{PDF_DIR}/{filename}")

if __name__ == "__main__":
    generate_csvs()
    generate_pdfs()
    print("All data generated successfully.")
