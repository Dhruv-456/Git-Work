import pygame
import sys
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Sample Bollywood movie dataset (title, description)
movies = [
    ("Mission Impossible", "action drama thriller suspense friendship"),
    ("Ghosted", "action drama romance adventure"),
    ("Dishoom", "action drama adventure friendship"),
    ("Abhay", "action thriller crimes secrets"),
    ("Inception", "sci-fi thriller mystery action mind-bending"),
    ("The Dark Knight", "action drama superhero crime intense"),
    ("Titanic", "romance drama tragedy historical emotional"),
    ("Interstellar", "sci-fi space drama adventure emotional"),
    ("Jumanji", "adventure comedy action fantasy friendship"),
    ("Avengers: Endgame", "action superhero sci-fi drama emotional"),
    ("The Matrix", "sci-fi action thriller cyberpunk futuristic"),
    ("John Wick", "action thriller revenge assassin stylish"),
    ("The Notebook", "romance drama emotional love story"),
    ("The Conjuring", "horror thriller supernatural suspense scary"),
    ("Parasite", "thriller drama mystery satire social"),
    ("The Godfather", "crime drama classic family mafia"),
    ("The Shawshank Redemption", "drama prison friendship hope inspirational"),
    ("Forrest Gump", "drama comedy emotional romance inspirational"),
    ("Black Panther", "action superhero drama african-heritage cultural"),
    ("Frozen", "animation musical fantasy friendship family"),
    ("The Lion King", "animation drama musical animals coming-of-age"),
    ("Shrek", "animation comedy fantasy adventure friendship"),
    ("Finding Nemo", "animation adventure family underwater emotional"),
    ("Gladiator", "action drama historical revenge epic"),
    ("The Revenant", "adventure drama survival revenge action"),
    ("Spider-Man: No Way Home", "superhero action drama multiverse emotional"),
    ("The Pursuit of Happyness", "biography drama emotional inspirational family"),
    ("La La Land", "romance musical drama dreams sacrifice"),
    ("Joker", "drama thriller psychological crime disturbing"),
    ("Tenet", "sci-fi action thriller mind-bending time-travel"),
    ("No Time to Die", "action thriller spy drama emotional"),
    ("Mad Max: Fury Road", "action adventure dystopian sci-fi intense"),
    ("Dangal", "sports drama biography inspirational family"),
    ("3 Idiots", "comedy drama friendship education inspirational"),
    ("PK", "comedy drama sci-fi satire social"),
    ("Drishyam", "thriller crime drama family suspense"),
    ("Andhadhun", "thriller comedy crime twist musical"),
    ("RRR", "action drama friendship historical patriotic"),
    ("Pathaan", "action spy drama patriotism thriller"),
    ("Bajrangi Bhaijaan", "drama emotional comedy patriotism humanity"),
    ("Kantara", "drama mythological action folklore mystery"),
    ("K.G.F: Chapter 1", "action drama crime rise power gritty"),
    ("War", "action thriller spy betrayal twists"),
    ("Don", "action crime drama thriller mafia"),
    ("Barfi!", "romance comedy drama emotional heartwarming"),
    ("Zindagi Na Milegi Dobara", "drama friendship adventure self-discovery"),
    ("Queen", "comedy drama self-discovery empowerment travel"),
    ("Tumbbad", "horror thriller fantasy mythology greed"),
    ("The Lunchbox", "romance drama emotional slice-of-life subtle"),
    ("Swades", "drama emotional patriotism inspirational rural"),
]

# Extract titles and descriptions
titles = [title for title, desc in movies]
descriptions = [desc for title, desc in movies]

# Vectorize the descriptions
vectorizer = TfidfVectorizer()
tfidf_matrix = vectorizer.fit_transform(descriptions)

# Compute cosine similarity matrix
cosine_sim = cosine_similarity(tfidf_matrix)

# Recommendation function
def recommend(title, top_n=5):
    # Convert input title to a standardized format (e.g., title case or lowercase)
    # and compare with standardized titles in the database for robust matching.
    # For simplicity, let's just convert both to lower for comparison.
    input_title_lower = title.lower()
    
    # Find a matching title from our list (case-insensitive)
    matched_idx = -1
    for i, t in enumerate(titles):
        if t.lower() == input_title_lower:
            matched_idx = i
            break
            
    if matched_idx == -1:
        return ["Movie not found in database. Please check the spelling."]

    sim_scores = list(enumerate(cosine_sim[matched_idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    recommendations = []
    # Start from 1 to exclude the movie itself
    for i, score in sim_scores[1:top_n+1]:
        recommendations.append(f"{titles[i]} (Similarity: {score:.2f})")
    return recommendations

# Pygame setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Bollywood Movie Recommendation System")

# Colors
WHITE = (255, 255, 255)
LIGHT_GRAY = (240, 240, 240)
GRAY = (200, 200, 200)
DARK_GRAY = (50, 50, 50)
BLACK = (0, 0, 0)
BLUE = (100, 149, 237)
DARK_BLUE = (70, 130, 180) 
BG_TOP = (255, 200, 200) # Light pinkish gradient top
BG_BOTTOM = (200, 220, 255) # Light pinkish gradient bottom

# Fonts
font = pygame.font.SysFont("Arial", 24)
big_font = pygame.font.SysFont("Arial", 36, bold=True)
title_font = pygame.font.SysFont("Arial", 28, bold=True)

# Input Box
input_box = pygame.Rect(50, 80, 700, 45)
input_text = ''
active = False

# Button
button_rect = pygame.Rect(330, 140, 140, 45)

# Output Area
output_box = pygame.Rect(50, 220, 700, 250)
recommendations = []

def draw_rounded_rect(surface, color, rect, radius=10):
    """Draw a rounded rectangle."""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_gradient_background(surface, top_color, bottom_color):
    """Draw a vertical gradient background."""
    for y in range(HEIGHT):
        blend = y / HEIGHT
        r = int(top_color[0] * (1 - blend) + bottom_color[0] * blend)
        g = int(top_color[1] * (1 - blend) + bottom_color[1] * blend)
        b = int(top_color[2] * (1 - blend) + bottom_color[2] * blend)
        pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

running = True
while running:
    draw_gradient_background(screen, BG_TOP, BG_BOTTOM)

    # Draw the Title
    header = title_font.render("Bollywood Movie Recommendation System", True, DARK_GRAY)
    screen.blit(header, (WIDTH // 2 - header.get_width() // 2, 20))

    # Draw the input label
    label = font.render("Enter Movie Title:", True, BLACK)
    screen.blit(label, (50, 50))

    # Draw the input box
    draw_rounded_rect(screen, WHITE, input_box, radius=8)
    pygame.draw.rect(screen, BLUE if active else GRAY, input_box, 2, border_radius=8)
    txt_surface = font.render(input_text, True, BLACK)
    screen.blit(txt_surface, (input_box.x + 10, input_box.y + 10))

    # Draw the button
    button_color = DARK_BLUE
    button_text_color = WHITE
    if button_rect.collidepoint(pygame.mouse.get_pos()): # Simple hover effect
        button_color = BLUE 
    draw_rounded_rect(screen, button_color, button_rect, radius=8)
    button_text = font.render("Recommend", True, button_text_color)
    screen.blit(button_text, (button_rect.x + (button_rect.width - button_text.get_width()) // 2, 
                               button_rect.y + (button_rect.height - button_text.get_height()) // 2))


    # Draw the output box
    draw_rounded_rect(screen, WHITE, output_box, radius=10)
    pygame.draw.rect(screen, DARK_BLUE, output_box, 2, border_radius=10)

    # Display recommendations
    y = output_box.y + 20
    if recommendations:
        result_label = font.render("Top Recommendations:", True, BLACK)
        screen.blit(result_label, (output_box.x + 20, y))
        y += 40
        for rec in recommendations:
            # Draw bullet point
            bullet_x = output_box.x + 30
            bullet_y = y + 10
            pygame.draw.circle(screen, DARK_BLUE, (bullet_x, bullet_y), 5)
            rec_text = font.render(rec, True, DARK_GRAY)
            screen.blit(rec_text, (bullet_x + 20, y))
            y += 30 # Move to the next line for the next recommendation

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if input_box.collidepoint(event.pos):
                active = True
            else:
                active = False
            if button_rect.collidepoint(event.pos):
                if input_text.strip():
                    recommendations = recommend(input_text.strip())
                else:
                    recommendations = ["Please enter a movie title."]

        elif event.type == pygame.KEYDOWN:
            if active:
                if event.key == pygame.K_RETURN:
                    if input_text.strip():
                        recommendations = recommend(input_text.strip())
                    else:
                        recommendations = ["Please enter a movie title."]
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                else:
                    input_text += event.unicode

    pygame.display.flip()

pygame.quit()
sys.exit()