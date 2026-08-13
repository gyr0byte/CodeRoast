"""
CodeRoast — Roast Templates
All roast templates organized by category.

Each category maps to a list of template strings.
Templates use {placeholder} syntax for dynamic values from metrics.

Categories:
    - high_complexity  → cyclomatic complexity > 10
    - bad_naming       → naming score < 60
    - no_comments      → comment ratio < 0.05
    - too_long         → avg function length > 50
    - deep_nesting     → nesting depth > 5
    - duplicate_code   → duplication score < 50
    - too_few_functions → only 1 giant function
    - praise           → genuinely good code (rare)
    - general          → fallback roasts
    - syntax_error     → code couldn't even be parsed
"""

ROAST_TEMPLATES = {
    # ── Cyclomatic Complexity ────────────────────────────────────────────
    "high_complexity": [
        "This function has a cyclomatic complexity of {score}. So does my anxiety. Neither is healthy.",
        "I've seen spaghetti with less nesting than this. And at least spaghetti is delicious.",
        "Your function does {count} things. So does a Swiss Army knife. At least the knife is intentional.",
        "This code has more branches than a decision tree. Actually, it IS a decision tree. A bad one.",
        "I counted {score} paths through this function. NASA uses fewer trajectories to reach Mars.",
        "Your if-else chain is so long, it has its own table of contents.",
        "This function doesn't need a refactor. It needs an intervention.",
        "This is less of a function and more of a choose-your-own-adventure book where every ending is a stack overflow.",
        "If I print this control flow graph, it looks like a Jackson Pollock painting. But less valuable.",
        "Your code complexity is higher than my electric bill during a GPU training run.",
    ],

    # ── Bad Naming ───────────────────────────────────────────────────────
    "bad_naming": [
        "Variable named '{name}'? Bold choice. Did you lose a bet?",
        "I see you named your function '{name}'. I've seen more descriptive cave paintings.",
        "'{name}' tells me absolutely nothing about what this does. Neither does reading the function body, to be fair.",
        "Using single-letter variable names is not 'minimalism'. It is 'job security through obscurity'.",
        "Your naming convention appears to be 'keyboard smash'. Innovative, but not recommended.",
        "I've seen better naming conventions in a toddler's crayon drawings.",
        "Your variables are named like witness protection participants. Nobody can identify them.",
        "Naming things is hard, but naming a list of users `stuff` is just giving up on life.",
        "A variable named `temp2_final_v3`? I see you follow the Photoshop file naming convention.",
        "Your function names are longer than the code inside them. Let's find a middle ground.",
    ],

    # ── No Comments ──────────────────────────────────────────────────────
    "no_comments": [
        "Zero comments. Future you will hate present you. It is a rite of passage at this point.",
        "I assume the lack of comments means the code is so self-explanatory that... wait, no it is not.",
        "No comments detected. I see you like to live dangerously.",
        "This code has fewer comments than a library during finals week. And that is saying something.",
        "Documentation? Never heard of her. Apparently neither have you.",
        "Comment ratio: {ratio}%. That is not minimalism. That is negligence.",
        "I see you didn't write comments because 'the code is the documentation.' Bold assumption.",
        "No comments? I guess you want to keep the mystery alive. Spoiler alert: the ending is terrible.",
        "Leaving no comments is a great way to ensure nobody takes over your code. Ever.",
    ],

    # ── Functions Too Long ───────────────────────────────────────────────
    "too_long": [
        "This function is {lines} lines long. So is the list of things wrong with it.",
        "At {lines} lines, this function has more responsibilities than I do. And I'm an AI.",
        "Your function is {lines} lines. That is not a function. That is a short story.",
        "I've read novellas shorter than this function. At least those had character development.",
        "This function is so long, it should have its own README.",
        "{lines} lines in one function. The Single Responsibility Principle just filed a restraining order.",
        "This function spans {lines} lines. It has its own timezone at the bottom.",
        "At {lines} lines, this function is longer than the user agreement nobody reads.",
        "This code block is so long it violates the Geneva Convention on readability.",
    ],

    # ── Deep Nesting ─────────────────────────────────────────────────────
    "deep_nesting": [
        "Nesting depth: {depth}. This code is deeper than my existential crisis.",
        "I found {depth} levels of nesting. Even Inception only went 4 levels deep.",
        "Your indentation goes so far right, it is about to fall off the screen.",
        "This nesting depth qualifies as a spelunking expedition. Bring a headlamp.",
        "Arrow code detected. Your code points to the right like it is trying to escape the file.",
        "Indentation level: {depth}. Are you trying to write code or build a staircase to heaven?",
        "At {depth} nested blocks, your code has more layers than an onion. And it's making me cry.",
    ],

    # ── Duplicate Code ───────────────────────────────────────────────────
    "duplicate_code": [
        "I found duplicate code blocks. Copy-paste is not a design pattern.",
        "This code has more repetition than a pop song chorus. At least pop songs are catchy.",
        "DRY stands for Don't Repeat Yourself. Apparently you thought it meant Do Repeat Yourself.",
        "Your code has the same block repeated multiple times. Functions exist. Use them.",
        "I see you believe in the ancient art of copy-paste engineering. Bold strategy.",
        "Duplicate blocks detected. Copy-pasting isn't reuse, it's just spreading the infection.",
        "I found identical code blocks. Ctrl+C and Ctrl+V are not architectural tools.",
    ],

    # ── Too Few Functions ────────────────────────────────────────────────
    "too_few_functions": [
        "Your entire program is in one function. That is not code. That is a monologue.",
        "Function count: {count}. Even 'Hello World' programs have more structure.",
        "One function to rule them all, one function to find them, one function to bring them all, and in the darkness bind them.",
        "You wrote {lines} lines with {count} function(s). That ratio concerns me deeply.",
        "One giant function to rule them all. OOP developers are crying somewhere.",
        "You put all your eggs in one monolithic basket. Hope you like omelets.",
    ],

    # ── Praise (for genuinely good code) ─────────────────────────────────
    "praise": [
        "Wait. This is actually decent. I need a moment. I was not prepared for this.",
        "Clean code detected. Are you sure you wrote this?",
        "I... I don't have anything mean to say. This is a first. Are you a compiler in disguise?",
        "Well-structured, well-named, well-commented. Who hurt you into writing good code?",
        "Your code is clean. Suspiciously clean. I will be watching you.",
        "This code is so clean, it made me question my purpose as a roasting AI.",
        "Well, well, well. Someone actually knows what they're doing. I'm almost bored.",
        "Clean, readable, concise. Did you copy this from Stack Overflow?",
        "This code is so clean I could eat off it. Beautiful work.",
    ],

    # ── General / Fallback ───────────────────────────────────────────────
    "general": [
        "I have analyzed your code. I have questions. Mostly 'why'.",
        "Your code works. That is the nicest thing I can say about it.",
        "On a scale of 'beautiful' to 'war crime', this is somewhere around 'parking violation'.",
        "I have seen things. Your code is now one of those things.",
        "This code passes. Like a kidney stone passes. Technically successful, but painful for everyone involved.",
        "Your code is like a mystery novel. No one knows what it does, including the author.",
        "I've seen worse code, but usually in museum exhibits of what not to do.",
        "This looks like code written by a committee that couldn't agree on anything.",
        "Your code is the software equivalent of 'it works on my machine'.",
    ],

    # ── Syntax Error ─────────────────────────────────────────────────────
    "syntax_error": [
        "Your code has a syntax error. I cannot roast what cannot run.",
        "SyntaxError detected. The code roasted itself. My work here is done.",
        "I tried to analyze your code, but Python refused to parse it. Even the interpreter gave up on you.",
        "Your code has syntax errors. It is not just bad code. It is not even code.",
        "This code has syntax errors. You roasted it yourself before I could even try.",
        "Syntax error. My parser walked out on strike.",
    ],
}


# ── Severity Modifiers ──────────────────────────────────────────────────────
# These are appended based on severity level to amplify the roast.
SEVERITY_MODIFIERS = {
    1: [  # Gentle
        "But hey, we all start somewhere.",
        "Keep going, you will get there.",
        "Not the worst I have seen. Not the best either.",
        "Still, you've got potential.",
        "Keep practicing, Rome wasn't built in a day.",
    ],
    2: [  # Standard
        "Do better.",
        "Your code needs a therapist.",
        "I am not angry. I am just disappointed.",
        "Seriously, refactor this before anyone else sees it.",
        "My disappointment is immeasurable, and my day is ruined.",
    ],
    3: [  # No Mercy
        "Delete this. Start over. Consider a career change.",
        "This code is a crime against computing.",
        "I showed this to other AIs. They are still laughing.",
        "git reset --hard HEAD~999. Trust me.",
        "This belongs in a trash can, not a repository.",
        "Go back to Hello World and take it slow this time.",
    ],
}


# ── Grade Reactions ─────────────────────────────────────────────────────────
# One-liner reactions shown alongside the letter grade.
GRADE_REACTIONS = {
    "S": "I do not trust this. Running additional scans...",
    "A": "Not bad. I am almost impressed. Almost.",
    "B": "It works, but so does a duct-taped pipe.",
    "C": "This grade stands for 'Concerning', which it is.",
    "D": "The 'D' stands for 'Deeply Troubling'. And also 'D'.",
    "F": "F is for 'Fire'. As in, set this code on fire.",
}
