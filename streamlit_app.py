import streamlit as st
import pandas as pd
import random


# Load the vocabulary data
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        # Validate the CSV structure
        required_columns = ["word", "translation", "definition", "example_usage"]
        if not all(col in df.columns for col in required_columns):
            raise ValueError(
                "CSV file must contain 'word', 'translation', 'definition', and 'example_usage' columns."
            )
        return df
    except FileNotFoundError:
        st.error(f"Error: File '{file_path}' not found.")
        return None
    except pd.errors.EmptyDataError:
        st.error(f"Error: File '{file_path}' is empty.")
        return None
    except pd.errors.ParserError:
        st.error(
            f"Error: Could not parse '{file_path}'. Please ensure it's a valid CSV file."
        )
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

    # File upload
    uploaded_file = st.file_uploader("Upload your vocabulary CSV file", type=["csv"])

    if uploaded_file is not None:
        df = load_data(uploaded_file)

        if df is not None:
            # Initialize session state variables if they don't exist
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
            if "choices" not in st.session_state:
                st.session_state.choices = None

            # Start quiz or show word details
            if (
                st.session_state.current_question is None
                and not st.session_state.show_details
            ):
                if st.button("Start Quiz"):
                    st.session_state.current_question = generate_question(df)
                    st.session_state.score = 0
                    st.session_state.question_number = 1
                    st.session_state.user_answer = None
                    st.session_state.choices = None

            if st.session_state.current_question is not None:
                definition, correct_word, choices = st.session_state.current_question
                st.write(f"Question {st.session_state.question_number}:")
                st.write(f"**Definition:** {definition}")

                # Store choices in session state
                if (
                    "choices" not in st.session_state
                    or st.session_state.choices is None
                ):
                    st.session_state.choices = choices

                # Use a placeholder for the radio buttons
                radio_placeholder = st.empty()

                # Display radio buttons using the placeholder
                selected_answer = radio_placeholder.radio(
                    "Choose the correct word:", st.session_state.choices
                )

                # Update user_answer in session state only if a different answer is selected
                if selected_answer != st.session_state.user_answer:
                    st.session_state.user_answer = selected_answer

                # Submit button logic (with disabling)
                submit_disabled = st.session_state.get(
                    "user_answer", None
                ) is None or st.session_state.get("show_details", True)

                def on_click_submit():
                    if st.session_state.user_answer == correct_word:
                        st.session_state.score += 1
                        st.success("Correct!")
                    else:
                        st.error(f"Incorrect. The correct word was: {correct_word}")
                    st.session_state.show_details = True

                st.button(
                    "Submit Answer", disabled=submit_disabled, on_click=on_click_submit
                )

                # Always show details if show_details is True
                if st.session_state.show_details:
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
                        st.session_state.choices = None

                    st.button("Next Question", on_click=on_next_question)

            # Display score
            st.write(
                f"Score: {st.session_state.score} / {st.session_state.question_number -1 if st.session_state.question_number > 1 else 0}"
            )

            # View Vocabulary List
            if st.checkbox("View Vocabulary List"):
                st.write(df)

            # Reset the quiz
            if st.button("Reset Quiz"):
                st.session_state.current_question = None
                st.session_state.score = 0
                st.session_state.question_number = 1
                st.session_state.show_details = False
                st.session_state.user_answer = None
                st.session_state.choices = None


if __name__ == "__main__":
    main()
