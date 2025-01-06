import os

import streamlit as st
import pandas as pd
import random

# Load the vocabulary data
@st.cache_data
def load_data(file=None, fallback_filename=None):
    """
    Loads a CSV file from either an uploaded file (file-like object)
    or from a fallback path if no file is provided.
    """
    try:
        if file is not None:
            # If user uploaded a file, read from that directly
            df = pd.read_csv(file)
        else:
            # Otherwise, load the local CSV in the same directory as this script
            script_dir = os.path.dirname(__file__)
            file_path = os.path.join(script_dir, fallback_filename)
            df = pd.read_csv(file_path)

        # Validate the CSV columns
        required_columns = ["word", "translation", "definition", "example_usage"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                "CSV file must contain 'word', 'translation', 'definition', "
                "and 'example_usage' columns."
            )
        return df

    except FileNotFoundError:
        st.error(f"Error: File not found. Please upload a file or place '{fallback_filename}' in the script directory.")
        return None
    except pd.errors.EmptyDataError:
        st.error("Error: The CSV file is empty.")
        return None
    except pd.errors.ParserError:
        st.error("Error: Could not parse the CSV file. Please ensure it is valid.")
        return None
    except ValueError as e:
        st.error(f"Error: {e}")
        return None



# Function to generate quiz questions
def generate_question(df):
    row = df.sample(1).iloc[0]
    correct_word = row["word"]
    definition = row["definition"]
    choices = [correct_word] + random.sample(df["word"].tolist(), 3)
    random.shuffle(choices)
    return definition, correct_word, choices


# Function to show word details
def show_word_details(df, word):
    word_row = df[df["word"] == word].iloc[0]
    st.write(f"**Word:** {word_row['word']}")
    st.write(f"**Chinese Word:** {word_row['translation']}")
    st.write(f"**Definition:** {word_row['definition']}")
    st.write(f"**Example Usage:** {word_row['example_usage']}")


def main():
    st.title("Vocabulary Quiz App")

    uploaded_file = st.file_uploader("Upload your vocabulary CSV file", type=["csv"])

    # If the user hasn't uploaded a file, fallback to local "data.csv"
    if uploaded_file is None:
        st.info("No file uploaded. Using Emily's vocabulary list.")
        df = load_data(fallback_filename="default_vocab.csv")
    else:
        df = load_data(file=uploaded_file, fallback_filename="default_vocab.csv")

    # If df is None at this point, there's an error, so don't proceed
    if df is None:
        st.stop()

    if "current_question" not in st.session_state:
        st.session_state.current_question = None
    if "score" not in st.session_state:
        st.session_state.score = 0
    if "question_number" not in st.session_state:
        st.session_state.question_number = 1
    if "show_details" not in st.session_state:
        st.session_state.show_details = False
    if "user_answer" not in st.session_state:
        st.session_state.user_answer = None
    # Store message in session state
    if "result_message" not in st.session_state:
        st.session_state.result_message = ""

    if (
        st.session_state.current_question is None
        and not st.session_state.show_details
    ):
        if st.button("Start Quiz"):
            st.session_state.current_question = generate_question(df)
            st.session_state.score = 0
            st.session_state.question_number = 1
            st.session_state.user_answer = None
            st.session_state.result_message = ""

    if st.session_state.current_question is not None:
        definition, correct_word, choices = st.session_state.current_question

        st.write(f"Question {st.session_state.question_number}:")
        st.write(f"**Definition:** {definition}")

        # Display the message below the question
        # (This is re-rendered on every script run, so you'll see 
        #  updates to st.session_state.result_message.)
        st.markdown(st.session_state.result_message, unsafe_allow_html=True)

        selected_answer = st.radio(
            "Choose the correct word:", 
            options=choices,
            key="user_answer"  # Ties this radio to session_state["user_answer"]
        )

        def on_click_submit():
            if st.session_state.user_answer == correct_word:
                st.session_state.score += 1
                st.session_state.result_message = (
                    "<span style='color:green'>Correct!</span>"
                )
            else:
                st.session_state.result_message = (
                    f"<span style='color:red'>Incorrect. "
                    f"The correct word was: {correct_word}</span>"
                )
            st.session_state.show_details = True

        st.button("Submit Answer", on_click=on_click_submit)

        if st.session_state.show_details:
            # Show the details
            show_word_details(
                df,
                correct_word 
                if st.session_state.user_answer == correct_word
                else st.session_state.user_answer,
            )

            def on_next_question():
                st.session_state.question_number += 1
                st.session_state.current_question = generate_question(df)
                st.session_state.show_details = False
                st.session_state.user_answer = None
                st.session_state.result_message = ""

            st.button("Next Question", on_click=on_next_question)

    # Show the score
    current_num = st.session_state.question_number - 1
    if current_num < 0:
        current_num = 0
    st.write(f"Score: {st.session_state.score} / {current_num}")

    if st.checkbox("View Vocabulary List"):
        st.write(df)

    # Reset
    if st.button("Reset Quiz"):
        st.session_state.current_question = None
        st.session_state.score = 0
        st.session_state.question_number = 1
        st.session_state.show_details = False
        st.session_state.user_answer = None
        st.session_state.result_message = ""

if __name__ == "__main__":
    main()
