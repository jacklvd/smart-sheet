import re
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from collections import defaultdict
from heapq import nlargest
from utils.text_processor import count_words, clean_text


class TextSummarizer:
    """Class that provides text summarization functionality with improved error handling"""

    def __init__(self):
        # Try to get stopwords, with fallback if not available
        try:
            self.stop_words = set(stopwords.words("english"))
        except Exception as e:
            print(f"Warning: Could not load stopwords: {e}")
            # Fallback to a basic set of common English stopwords
            self.stop_words = {
                "a",
                "an",
                "the",
                "and",
                "but",
                "if",
                "or",
                "because",
                "as",
                "until",
                "while",
                "of",
                "at",
                "by",
                "for",
                "with",
                "about",
                "against",
                "between",
                "into",
                "through",
                "during",
                "before",
                "after",
                "above",
                "below",
                "to",
                "from",
                "up",
                "down",
                "in",
                "out",
                "on",
                "off",
                "over",
                "under",
                "again",
                "further",
                "then",
                "once",
                "here",
                "there",
                "when",
                "where",
                "why",
                "how",
                "all",
                "any",
                "both",
                "each",
                "few",
                "more",
                "most",
                "other",
                "some",
                "such",
                "no",
                "nor",
                "not",
                "only",
                "own",
                "same",
                "so",
                "than",
                "too",
                "very",
                "s",
                "t",
                "can",
                "will",
                "just",
                "don",
                "don't",
                "should",
                "now",
                "d",
                "ll",
                "m",
                "o",
                "re",
                "ve",
                "y",
                "ain",
                "aren",
                "aren't",
                "couldn",
                "couldn't",
                "didn",
                "didn't",
                "doesn",
                "doesn't",
                "hadn",
                "hadn't",
                "hasn",
                "hasn't",
                "haven",
                "haven't",
                "isn",
                "isn't",
                "ma",
                "mightn",
                "mightn't",
                "mustn",
                "mustn't",
                "needn",
                "needn't",
                "shan",
                "shan't",
                "shouldn",
                "shouldn't",
                "wasn",
                "wasn't",
                "weren",
                "weren't",
                "won",
                "won't",
                "wouldn",
                "wouldn't",
            }

    def summarize(self, text, max_length=None, summary_type="concise"):
        """
        Summarize the given text with improved error handling

        Args:
            text (str): The text to summarize
            max_length (int, optional): Maximum length of summary in words
            summary_type (str): 'concise' or 'detailed' summary

        Returns:
            dict: Summary result including the summarized text and statistics
        """
        try:
            # Input validation
            if not isinstance(text, str):
                raise ValueError("Text must be a string")

            if not text or not text.strip():
                return {
                    "summary": "",
                    "original_length": 0,
                    "summary_length": 0,
                }

            # Clean and prepare the text
            try:
                cleaned_text = clean_text(text)
            except Exception as e:
                print(f"Warning: Error during text cleaning: {e}")
                cleaned_text = text  # Fallback to original text

            # Handle very short texts
            if len(cleaned_text.strip()) < 100:
                return {
                    "summary": cleaned_text,
                    "original_length": count_words(text),
                    "summary_length": count_words(cleaned_text),
                }

            # Tokenize the text into sentences with error handling
            try:
                sentences = sent_tokenize(cleaned_text)
                if not sentences:
                    # If tokenization fails, fallback to simple splitting
                    sentences = [
                        s.strip()
                        for s in re.split(r"[.!?]+", cleaned_text)
                        if s.strip()
                    ]
            except Exception as e:
                print(f"Warning: Error during sentence tokenization: {e}")
                # Fallback to simple sentence splitting
                sentences = [
                    s.strip() for s in re.split(r"[.!?]+", cleaned_text) if s.strip()
                ]

            if not sentences:
                return {
                    "summary": cleaned_text,
                    "original_length": count_words(text),
                    "summary_length": count_words(cleaned_text),
                }

            # Set max_length if not provided or invalid
            try:
                if max_length is not None:
                    max_length = int(max_length)
                    if max_length <= 0:
                        max_length = None
            except (ValueError, TypeError):
                max_length = None

            if not max_length:
                try:
                    original_word_count = count_words(cleaned_text)
                    if summary_type == "concise":
                        # Concise summary: 20-30% of original length
                        max_length = max(30, min(int(original_word_count * 0.3), 200))
                    else:
                        # Detailed summary: 40-60% of original length
                        max_length = max(50, min(int(original_word_count * 0.6), 500))
                except Exception as e:
                    print(f"Warning: Error calculating max_length: {e}")
                    # Fallback to safe default
                    max_length = 100 if summary_type == "concise" else 200

            # Calculate sentence scores with error handling
            try:
                sentence_scores = self._score_sentences(sentences, summary_type)
            except Exception as e:
                print(f"Warning: Error scoring sentences: {e}")
                # Fallback to equal weights for all sentences
                sentence_scores = {i: 1.0 for i in range(len(sentences))}

            # Select top sentences with error handling
            try:
                summary_sentences = self._select_top_sentences(
                    sentences, sentence_scores, max_length
                )
            except Exception as e:
                print(f"Warning: Error selecting top sentences: {e}")
                # Fallback to first few sentences that fit within max_length
                summary_sentences = []
                words_so_far = 0
                for sent in sentences:
                    words_in_sent = count_words(sent)
                    if words_so_far + words_in_sent <= max_length:
                        summary_sentences.append(sent)
                        words_so_far += words_in_sent
                    else:
                        break

            # Ensure we have something in the summary
            if not summary_sentences and sentences:
                summary_sentences = [
                    sentences[0]
                ]  # At least include the first sentence

            # Combine sentences into summary
            summary = " ".join(summary_sentences)

            # Ensure summary is not empty
            if not summary.strip():
                summary = (
                    cleaned_text[:500] + "..."
                    if len(cleaned_text) > 500
                    else cleaned_text
                )

            return {
                "summary": summary,
                "original_length": count_words(text),
                "summary_length": count_words(summary),
            }

        except Exception as e:
            print(f"Error in summarize method: {str(e)}")
            # Return a safe fallback
            return {
                "summary": text[:500] + "..." if len(text) > 500 else text,
                "original_length": len(text.split()),
                "summary_length": min(len(text.split()), 100),
                "error": f"Summarization failed: {str(e)}",
            }

    def _score_sentences(self, sentences, summary_type):
        """
        Score sentences based on importance with improved error handling

        Args:
            sentences (list): List of sentences
            summary_type (str): Type of summary to generate

        Returns:
            dict: Dictionary of sentence scores
        """
        try:
            # Combine all sentences into a single text for word frequency analysis
            full_text = " ".join(sentences)

            # Tokenize and remove stop words
            try:
                words = word_tokenize(full_text.lower())
            except Exception as e:
                print(f"Warning: Error tokenizing words: {e}")
                # Fallback to simple word splitting
                words = re.findall(r"\b\w+\b", full_text.lower())

            word_freq = FreqDist(
                word for word in words if word.isalnum() and word not in self.stop_words
            )

            # Max word frequency for normalization
            max_freq = max(word_freq.values()) if word_freq else 1

            # Normalize word frequencies
            for word in word_freq:
                word_freq[word] = word_freq[word] / max_freq

            # Score sentences
            sentence_scores = defaultdict(float)

            for i, sentence in enumerate(sentences):
                try:
                    sent_words = word_tokenize(sentence.lower())
                except Exception:
                    # Fallback to simple word splitting
                    sent_words = re.findall(r"\b\w+\b", sentence.lower())

                for word in sent_words:
                    if word in word_freq:
                        # Add word importance to sentence score
                        sentence_scores[i] += word_freq[word]

                # Normalize by sentence length to avoid bias towards longer sentences
                # But not too much - we still want to favor information-rich sentences
                if len(sent_words) > 0:
                    divisor = (
                        len(sent_words) ** 0.5
                    )  # Square root for softer normalization
                    sentence_scores[i] = sentence_scores[i] / divisor

                # Position bias - earlier sentences often contain key information
                # But for detailed summaries, we want content from throughout the text
                if summary_type == "concise":
                    # Stronger position bias for concise summaries
                    position_weight = 1.0 if i == 0 else 0.95 ** (i)
                    sentence_scores[i] *= position_weight
                else:
                    # Gentler position bias for detailed summaries
                    position_weight = 1.0 if i == 0 else 0.98 ** (i)
                    sentence_scores[i] *= position_weight

            return sentence_scores

        except Exception as e:
            print(f"Error in _score_sentences: {str(e)}")
            # Return equal weights as fallback
            return {i: 1.0 for i in range(len(sentences))}

    def _select_top_sentences(self, sentences, sentence_scores, max_length):
        """
        Select top sentences for the summary based on scores and max length

        Args:
            sentences (list): List of sentences
            sentence_scores (dict): Dictionary of sentence scores
            max_length (int): Maximum length of summary in words

        Returns:
            list: Selected sentences for the summary
        """
        try:
            # Safety check for inputs
            if not sentences or not sentence_scores:
                return sentences[:1] if sentences else []

            # Get top sentences (by index) based on scores
            try:
                top_sentence_indices = nlargest(
                    len(sentences), sentence_scores, key=sentence_scores.get
                )
            except Exception as e:
                print(f"Warning: Error selecting top sentences: {e}")
                # Fallback to using the original order
                top_sentence_indices = list(range(min(5, len(sentences))))

            # Sort indices to maintain original order
            top_sentence_indices.sort()

            # Build summary, respecting max_length
            summary_sentences = []
            word_count = 0

            for i in top_sentence_indices:
                if i >= len(sentences):
                    continue  # Skip invalid indices

                sentence = sentences[i]
                try:
                    sentence_word_count = count_words(sentence)
                except Exception:
                    # Fallback word count
                    sentence_word_count = len(sentence.split())

                if word_count + sentence_word_count <= max_length:
                    summary_sentences.append(sentence)
                    word_count += sentence_word_count
                else:
                    break

            return summary_sentences

        except Exception as e:
            print(f"Error in _select_top_sentences: {str(e)}")
            # Return some sentences as fallback
            return sentences[: min(3, len(sentences))]
