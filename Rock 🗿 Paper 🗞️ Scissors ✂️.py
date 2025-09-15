Rock 🗿 Paper 🗞️ Scissors ✂️ - the classic hand game where:

Rock beats Scissors (crushes them)
Scissors beat Paper (cut it)
Paper beats Rock (wraps it)

enhanced version of Rock–Paper–Scissors in Python where you can play multiple rounds, keep score, and even choose when to quit:

import random

# Choices available
choices = ["rock", "paper", "scissors"]

# Function to determine the winner
def determine_winner(user_choice, computer_choice):
    if user_choice == computer_choice:
        return "tie"
    elif (user_choice == "rock" and computer_choice == "scissors") or \
         (user_choice == "scissors" and computer_choice == "paper") or \
         (user_choice == "paper" and computer_choice == "rock"):
        return "user"
    else:
        return "computer"

# Main game loop
def play_game():
    user_score = 0
    computer_score = 0
    round_number = 1
    
    print("Welcome to Rock-Paper-Scissors!")
    print("Type 'quit' to exit the game anytime.\n")
    
    while True:
        print(f"--- Round {round_number} ---")
        user_choice = input("Enter rock, paper, or scissors: ").lower()
        
        if user_choice == "quit":
            break
        
        if user_choice not in choices:
            print("Invalid choice. Try again.\n")
            continue
        
        computer_choice = random.choice(choices)
        print(f"Computer chose: {computer_choice}")
        
        winner = determine_winner(user_choice, computer_choice)
        if winner == "user":
            print("You win this round!\n")
            user_score += 1
        elif winner == "computer":
            print("Computer wins this round!\n")
            computer_score += 1
        else:
            print("This round is a tie!\n")
        
        print(f"Score -> You: {user_score} | Computer: {computer_score}\n")
        round_number += 1
    
    print("Thanks for playing!")
    print(f"Final Score -> You: {user_score} | Computer: {computer_score}")
    if user_score > computer_score:
        print("You won the game! 🎉")
    elif user_score < computer_score:
        print("Computer won the game! 🤖")
    else:
        print("It's a tie overall!")

# Start the game
play_game()


✅ Features:

Multiple rounds until the user quits.
Keeps track of your score and the computer’s score.
Declares the overall winner at the end.
