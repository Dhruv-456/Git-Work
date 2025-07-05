import pandas as pd
import numpy as np
import pygame
import sys
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Data Preparation
data = {
    'Age': [25, 35, 45, 50, 23, 31, 60, 40, 29, 52],
    'Income': [30000, 60000, 80000, 72000, 25000, 40000, 90000, 55000, 38000, 85000],
    'LoanAmount': [10000, 15000, 20000, 18000, 5000, 12000, 25000, 70000, 11000, 23000],
    'CreditHistory': ['Good', 'Good', 'Bad', 'Good', 'Bad', 'Good', 'Good', 'Bad', 'Good', 'Bad'],
    'EmploymentStatus': ['Employed', 'Self-employed', 'Unemployed', 'Employed', 'Unemployed',
                         'Employed', 'Retired', 'Self-employed', 'Employed', 'Unemployed'],
    'Default': ['No', 'No', 'Yes', 'No', 'Yes', 'No', 'No', 'Yes', 'No', 'Yes']
}

df = pd.DataFrame(data)

# Encode categorical features
le_credit = LabelEncoder()
le_employment = LabelEncoder()
le_default = LabelEncoder()

df['CreditHistory'] = le_credit.fit_transform(df['CreditHistory'])
df['EmploymentStatus'] = le_employment.fit_transform(df['EmploymentStatus'])
df['Default'] = le_default.fit_transform(df['Default'])

X = df.drop('Default', axis=1)
y = df['Default']

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.3, random_state=42)

# Train model
model = LogisticRegression()
model.fit(X_train, y_train)

# Initialize Pygame
pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Credit Scoring Model")

font = pygame.font.SysFont(None, 30)
title_font = pygame.font.SysFont(None, 40)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200) # Added for prediction text

# Input boxes
inputs = {
    'Age': '',
    'Income': '',
    'LoanAmount': '',
    'CreditHistory': 'Good',  # default
    'EmploymentStatus': 'Employed'  # default
}

input_boxes = {
    'Age': pygame.Rect(200, 100, 140, 32),
    'Income': pygame.Rect(200, 150, 140, 32),
    'LoanAmount': pygame.Rect(200, 200, 140, 32),
}

dropdowns = {
    'CreditHistory': ['Good', 'Bad'],
    'EmploymentStatus': ['Employed', 'Self-employed', 'Unemployed', 'Retired']
}
dropdown_selected = {
    'CreditHistory': 0,
    'EmploymentStatus': 0
}

# Define dropdown rects based on their display positions
dropdown_rects = {
    'CreditHistory': pygame.Rect(200, 250, 140, 32),
    'EmploymentStatus': pygame.Rect(200, 300, 140, 32)
}


predict_button = pygame.Rect(200, 360, 200, 40) # Adjusted position to avoid overlap
confusion_button = pygame.Rect(200, 420, 200, 40) # Adjusted position

prediction_text = ''

# Main loop
active_field = None
running = True
while running:
    screen.fill(WHITE)

    # Title
    title = title_font.render("Credit Scoring Model", True, BLACK)
    screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 20))

    # Labels and inputs
    y_offset = 100
    for key in ['Age', 'Income', 'LoanAmount']:
        label = font.render(f"{key}:", True, BLACK)
        screen.blit(label, (50, y_offset))
        pygame.draw.rect(screen, GRAY if active_field == key else DARK_GRAY, input_boxes[key], 0)
        text_surface = font.render(inputs[key], True, BLACK)
        screen.blit(text_surface, (input_boxes[key].x + 5, input_boxes[key].y + 5))
        y_offset += 50

    # Dropdowns
    dropdown_label_credit = font.render("CreditHistory:", True, BLACK)
    screen.blit(dropdown_label_credit, (50, y_offset))
    dropdown_surface_credit = font.render(dropdowns['CreditHistory'][dropdown_selected['CreditHistory']], True, BLACK)
    pygame.draw.rect(screen, DARK_GRAY, dropdown_rects['CreditHistory'], 0) # Draw using the defined rect
    screen.blit(dropdown_surface_credit, (dropdown_rects['CreditHistory'].x + 5, dropdown_rects['CreditHistory'].y + 5))

    y_offset += 50
    dropdown_label_employment = font.render("EmploymentStatus:", True, BLACK)
    screen.blit(dropdown_label_employment, (50, y_offset))
    dropdown_surface_employment = font.render(dropdowns['EmploymentStatus'][dropdown_selected['EmploymentStatus']], True, BLACK)
    pygame.draw.rect(screen, DARK_GRAY, dropdown_rects['EmploymentStatus'], 0) # Draw using the defined rect
    screen.blit(dropdown_surface_employment, (dropdown_rects['EmploymentStatus'].x + 5, dropdown_rects['EmploymentStatus'].y + 5))

    # Buttons
    pygame.draw.rect(screen, GREEN, predict_button)
    predict_text_render = font.render("Predict Default", True, WHITE)
    screen.blit(predict_text_render, (predict_button.x + 20, predict_button.y + 5))

    pygame.draw.rect(screen, RED, confusion_button)
    confusion_text_render = font.render("Show Confusion Matrix", True, WHITE)
    screen.blit(confusion_text_render, (confusion_button.x + 5, confusion_button.y + 5))

    # Prediction Result
    prediction_display = font.render(f"Prediction: {prediction_text}", True, BLUE)
    screen.blit(prediction_display, (50, SCREEN_HEIGHT - 50))


    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            active_field = None # Reset active field on each click
            for key in input_boxes:
                if input_boxes[key].collidepoint(event.pos):
                    active_field = key
                    break

            # Dropdown toggles
            if dropdown_rects['CreditHistory'].collidepoint(event.pos):
                dropdown_selected['CreditHistory'] = (dropdown_selected['CreditHistory'] + 1) % len(dropdowns['CreditHistory'])
                inputs['CreditHistory'] = dropdowns['CreditHistory'][dropdown_selected['CreditHistory']] # Update input for consistency

            if dropdown_rects['EmploymentStatus'].collidepoint(event.pos):
                dropdown_selected['EmploymentStatus'] = (dropdown_selected['EmploymentStatus'] + 1) % len(dropdowns['EmploymentStatus'])
                inputs['EmploymentStatus'] = dropdowns['EmploymentStatus'][dropdown_selected['EmploymentStatus']] # Update input for consistency

            # Predict button
            if predict_button.collidepoint(event.pos):
                try:
                    # Collect inputs
                    input_data = {
                        'Age': float(inputs['Age']),
                        'Income': float(inputs['Income']),
                        'LoanAmount': float(inputs['LoanAmount']),
                        'CreditHistory': le_credit.transform([dropdowns['CreditHistory'][dropdown_selected['CreditHistory']]])[0],
                        'EmploymentStatus': le_employment.transform([dropdowns['EmploymentStatus'][dropdown_selected['EmploymentStatus']]])[0]
                    }

                    input_df = pd.DataFrame([input_data])
                    input_scaled = scaler.transform(input_df)
                    prediction = model.predict(input_scaled)[0]
                    prediction_text = 'Yes' if prediction == 1 else 'No'
                except ValueError:
                    prediction_text = "Error: Please enter valid numbers for Age, Income, and LoanAmount."
                except Exception as e:
                    prediction_text = f"Error: {e}"

            # Confusion button
            if confusion_button.collidepoint(event.pos):
                y_pred = model.predict(X_test)
                cm = confusion_matrix(y_test, y_pred)
                plt.figure(figsize=(6, 5)) # Create a figure before drawing
                sns.heatmap(cm, annot=True, fmt='d', cmap='Reds', xticklabels=le_default.classes_, yticklabels=le_default.classes_)
                plt.title("Confusion Matrix - Credit Scoring Model")
                plt.xlabel("Predicted")
                plt.ylabel("Actual")
                plt.tight_layout()
                plt.show()

        elif event.type == pygame.KEYDOWN and active_field:
            if event.key == pygame.K_BACKSPACE:
                inputs[active_field] = inputs[active_field][:-1]
            elif event.unicode.isdigit() or (event.unicode == '.' and '.' not in inputs[active_field]): # Allow numbers and one decimal for numerical fields
                if active_field in ['Age', 'Income', 'LoanAmount']:
                    inputs[active_field] += event.unicode
            elif event.unicode.isalpha(): # Allow letters for categorical fields if you had them (though not directly for these numerical inputs)
                pass # This block is not strictly needed for your current inputs as they are numerical or dropdowns


    pygame.display.flip()