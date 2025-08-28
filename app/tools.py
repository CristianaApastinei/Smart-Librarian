# app/tools.py

from typing import Dict

# Exact-title summaries used by the tool call.
# Make sure these titles match the ones you ingested in data/book_summaries.md.
BOOK_SUMMARIES: Dict[str, str] = {
    "1984": (
        "George Orwell’s dystopian novel set in Oceania, where the Party enforces "
        "total surveillance and ideological control under Big Brother. Winston Smith, "
        "a low-ranking clerk, secretly longs for truth and freedom and begins a doomed "
        "rebellion through love and forbidden thought. Themes: authoritarianism, truth, "
        "language, and resistance."
    ),
    "The Hobbit": (
        "J.R.R. Tolkien’s adventure tale about Bilbo Baggins, a comfort-loving hobbit "
        "recruited by Gandalf and a company of dwarves to reclaim their treasure from the "
        "dragon Smaug. Along the journey, Bilbo discovers courage, wit, and a surprising knack "
        "for heroism. Themes: adventure, growth, friendship, and resourcefulness."
    ),
    "To Kill a Mockingbird": (
        "Harper Lee’s classic set in the Depression-era American South, narrated by Scout Finch. "
        "Her father, Atticus, defends a Black man falsely accused of assault, exposing the town’s "
        "deep-seated racism while teaching Scout and Jem empathy and moral courage. Themes: justice, "
        "prejudice, innocence, and compassion."
    ),
    "The Catcher in the Rye": (
        "J.D. Salinger’s coming-of-age novel follows Holden Caulfield over a few wandering days "
        "in New York City after he leaves prep school. Cynical yet vulnerable, Holden grapples "
        "with loss, identity, and the ‘phoniness’ he perceives in adults. Themes: alienation, "
        "authenticity, grief, and adolescence."
    ),
    "The Lord of the Rings": (
        "Tolkien’s epic trilogy about a perilous quest to destroy the One Ring and defeat Sauron. "
        "A fellowship of unlikely heroes—hobbits, men, a dwarf, an elf, and a wizard—faces corrupting "
        "power, sacrifice, and temptation across Middle-earth. Themes: friendship, hope, duty, "
        "and the cost of power."
    ),
    "Pride and Prejudice": (
        "Jane Austen’s witty romance centered on Elizabeth Bennet and Mr. Darcy, whose initial "
        "misjudgments and social pride hinder affection. Through sharp social observation and lively "
        "dialogue, the novel explores class, character, and personal growth. Themes: love, reputation, "
        "prejudice, and self-knowledge."
    ),
    "Dune": (
        "Frank Herbert’s science-fiction saga set on Arrakis, a desert planet that produces the "
        "spice melange, the most valuable substance in the universe. Paul Atreides navigates "
        "political intrigue, ecological complexity, and messianic destiny among warring houses "
        "and the Fremen. Themes: power, prophecy, environment, and survival."
    ),
    "The Name of the Wind": (
        "Patrick Rothfuss’s fantasy framed as the autobiography of Kvothe—prodigy, magician, and "
        "musician—recounting his rise from tragedy to the University while pursuing the truth about "
        "the mysterious Chandrian. Themes: storytelling, identity, knowledge, and obsession."
    ),
    "The Little Prince": (
        "Antoine de Saint-Exupéry’s poetic fable in which a stranded pilot meets a curious prince "
        "from a small asteroid. Through whimsical encounters, the story reveals gentle wisdom about "
        "love, loss, imagination, and seeing with the heart. Themes: innocence, friendship, meaning, "
        "and perspective."
    ),
    "The Book Thief": (
        "Markus Zusak’s WWII novel narrated by Death, following Liesel Meminger, a girl in Nazi "
        "Germany who steals books and shares them, finding solace and connection amid brutality. "
        "Her foster family hides a Jewish man, deepening the risks and bonds they share. Themes: "
        "the power of words, humanity, courage, and compassion."
    ),
    "The Road": (
        "Cormac McCarthy’s stark post-apocalyptic journey of a father and son traveling through a "
        "ruined America. Facing scarcity and danger, they cling to love and a fragile moral code—"
        "‘carrying the fire’—in a world stripped bare. Themes: parental love, survival, morality, "
        "and hope against despair."
    ),
}

def get_summary_by_title(title: str) -> str:
    """
    Return the detailed summary for an exact book title.
    Titles must match the keys in BOOK_SUMMARIES (case-sensitive).
    """
    if not isinstance(title, str):
        return "Invalid title. Please provide a string."
    exact = title.strip()
    return BOOK_SUMMARIES.get(exact, "No detailed summary found for that exact title.")
