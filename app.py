from flask import Flask, render_template, request
import pandas as pd
import random
import os

app = Flask(__name__)

# Just making sure we have a place to stash uploads (even if unused)
app.config['UPLOAD_FOLDER'] = 'uploads'

# This function grabs 2 questions from different PARTs for each CO
def pick_questions(df, mark_type):
    final_questions = []
    cos_with_issues = []

    all_cos = sorted(df['CO MAPPING'].dropna().unique())

    for co in all_cos:
        # Filter by CO and mark type
        subset = df[(df['CO MAPPING'] == co) & (df['MARKS'] == mark_type)]
        unique_parts = subset['PART'].dropna().unique()

        # Need at least 2 different PARTs to proceed
        if len(unique_parts) < 2:
            cos_with_issues.append((co, mark_type))
            continue

        # Pick 2 different PARTs randomly
        chosen_parts = random.sample(list(unique_parts), 2)
        picked = []

        for part in chosen_parts:
            part_questions = subset[subset['PART'] == part]
            if not part_questions.empty:
                picked.append(part_questions.sample(1).iloc[0])

        if len(picked) == 2:
            final_questions.extend(picked)
        else:
            cos_with_issues.append((co, mark_type))

    return final_questions, cos_with_issues

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files.get('file')
        if not file:
            return "No file uploaded. Try again?", 400

        try:
