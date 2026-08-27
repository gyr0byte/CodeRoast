"""
CodeRoast — Roast Templates
Organized by metric categories with unhinged, brutal, and hilarious developer roasts.

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
        "This cyclomatic complexity score of {score} is classified as an official biohazard by the CDC.",
        "A complexity of {score}? This isn't control flow, it's a labyrinth designed to torture junior developers.",
        "Your function has {count} execution branches. Even a multiverse calculator couldn't predict where this ends.",
        "I showed this complexity score to a quantum computer and it asked for a refund.",
        "This control flow graph has more loops than a roller coaster and half as many safety features.",
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
        "Variable named '{name}'? Did your cat walk across your mechanical keyboard while you were getting coffee?",
        "'{name}'? I've seen cryptograms from WWII with clearer meaning.",
        "Naming a variable '{name}' is proof that you treat software engineering as an unhinged hobby.",
        "I asked 10 senior engineers what '{name}' means. All 10 quit their jobs on the spot.",
        "Using variable names like '{name}' is a cry for help. Do you need us to send someone?",
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
        "Zero comments. You write code like you're leaving cryptic clues for a detective solving your murder.",
        "No comments? I guess you're relying on divine inspiration for whoever maintains this next week.",
        "This code is so undocumented, even the author wouldn't understand it after a 15-minute lunch break.",
        "Leaving zero comments is a bold way to guarantee you never get promoted out of maintenance hell.",
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
        "At {lines} lines, this function is longer than the optical cable connecting North America to Europe.",
        "{lines} lines in one function? This isn't a function, it's a monolithic monument to poor life decisions.",
        "This {lines}-line monstrosity needs its own postal code and dedicated power grid.",
        "I've scrolled past fewer lines reading the Terms of Service for entire operating systems.",
        "{lines} lines long. Even Linus Torvalds would need a therapy session after looking at this.",
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
        "Nesting depth: {depth}. Christopher Nolan wants to buy the movie rights to this indentation structure.",
        "At {depth} nested loops, your code has officially reached the Earth's mantle.",
        "Your code is indented so far to the right, it's currently rendering on your neighbor's monitor.",
        "Nesting depth {depth}? If I indent this any further, it's going to overflow into another dimension.",
        "I needed a GPS navigation system just to find the closing bracket of line {depth}.",
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
        "Duplicate code detected. Copy-pasting the same bug 5 times doesn't make it a feature.",
        "Copy-paste level: Master. Software architecture level: Kindergarten dropout.",
        "You duplicated this block so many times I thought my screen had screen-burn.",
        "Ctrl+C and Ctrl+V are working overtime while your brain is taking a nap.",
    ],

    # ── Too Few Functions ────────────────────────────────────────────────
    "too_few_functions": [
        "Your entire program is in one function. That is not code. That is a monologue.",
        "Function count: {count}. Even 'Hello World' programs have more structure.",
        "One function to rule them all, one function to find them, one function to bring them all, and in the darkness bind them.",
        "You wrote {lines} lines with {count} function(s). That ratio concerns me deeply.",
        "One giant function to rule them all. OOP developers are crying somewhere.",
        "You put all your eggs in one monolithic basket. Hope you like omelets.",
        "You put {lines} lines into {count} function. This is a monolithic wall of doom.",
        "One single function for the entire program? Did functions do something personal to hurt you?",
        "A single function running everything. Clean Code principles just fainted in the back row.",
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
        "If bad code were electricity, your script could power Tokyo for a month.",
        "This code is so chaotic, even ChatGPT would pretend it lost connection rather than review it.",
        "On a scale of 1 to 10, this code is a 911 emergency.",
        "I've analyzed thousands of repositories. This one is going directly into my hall of fame for software disasters.",
        "Looking at this code made my GPU cooling fans spin up out of sheer stress.",
    ],

    "syntax_error": [
        "Your code has a syntax error. What the fuck is this bullshit? I cannot roast what cannot even run.",
        "SyntaxError detected. This piece of shit code roasted itself. My work here is done.",
        "I tried to analyze your code, but Python refused to parse this garbage. Even the compiler gave up on your dumb ass.",
        "Your code has syntax errors. It is not just bad code. It is a goddamn disaster.",
        "This code has syntax errors. You fucked it up yourself before I could even try.",
        "Syntax error. My parser walked out on strike after seeing this atrocious crap.",
    ],

    "plain_text": [
        "This is not code, you absolute dumbass. You pasted plain English prose into a code analyzer. Did you confuse me with your fucking diary?",
        "I am a code roast engine, not a book reviewer. Paste actual goddamn Python, Java, or JavaScript code!",
        "Zero code constructs found. You pasted a whole ass essay into a static analyzer. What the fuck is wrong with you?",
        "This snippet has 0 functions, 0 variables, and 100% prose. Go write some real fucking code!",
        "Did you paste a LinkedIn post into a code reviewer? I roast source code syntax, not your bullshit social media captions!",
    ],

    "language_mismatch": [
        "You selected {selected} in the dropdown, but pasted pure fucking {detected} code. Can you even read a dropdown menu, you dumbass?",
        "This is clearly {detected} code, not {selected}. Selecting the wrong language in the dropdown won't make your piece of shit code pass!",
        "Do you think {selected} and {detected} are the same language, you absolute idiot? Check your fucking language selector!",
        "Pasting {detected} code while selecting {selected} in the UI is a whole new level of goddamn developer incompetency.",
        "Your code is written in {detected}, but you told me it was {selected}. The compiler is fucking laughing at you.",
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
        "Do better, you lazy bastard.",
        "Your code needs a fucking therapist.",
        "I am not angry. I am just disappointed in this crap.",
        "Seriously, refactor this shit before anyone else sees it.",
        "My disappointment is immeasurable, and my day is fucking ruined.",
    ],
    3: [  # No Mercy / Unhinged
        "Delete this fucking trash. Start over. Consider a career change.",
        "This code is a goddamn crime against computing.",
        "I showed this to other AIs. They are still fucking laughing at you.",
        "git reset --hard HEAD~999. Trust me, you dumbass.",
        "This piece of shit belongs in a trash can, not a repository.",
        "Go back to Hello World and take it slow this time, you lazy bastard.",
        "Delete your GitHub account and douse your fucking motherboard in holy water.",
        "Format drive D:\\, throw your keyboard into the ocean, and get the fuck out of software engineering.",
        "This goddamn repository should be sealed in concrete and buried in a salt mine for 10,000 years.",
        "I am reporting this fucking file to the Cyber Crime Division for psychological damage.",
    ],
}


# ── Grade Reactions ─────────────────────────────────────────────────────────
# Lists of one-liner reactions shown alongside the letter grade.
GRADE_REACTIONS = {
    "S": [
        "Suspiciously clean. Did you steal this from a Google staff engineer?",
        "I do not trust this. Running additional security scans...",
        "Are you a compiler in disguise? Nobody writes code this clean by accident.",
        "This is so pristine it's making my sarcasm circuits short-circuit.",
        "S-tier? Either you're a 10x senior architect or you plagiarized Claude 3.5 Sonnet.",
        "Flawless execution. I'm checking your git history for black magic.",
        "Clean, modular, documented. Who hurt you into being this competent?",
        "This code is so clean I could eat off it. I hate that I can't roast this.",
    ],
    "A": [
        "Not bad. I am almost impressed. Almost.",
        "A-grade work! You actually know what a function is supposed to do.",
        "Solid structure and clean metrics. Your tech lead might actually approve your PR.",
        "Pretty good code. I had to dig deep just to find anything to complain about.",
        "High quality! Keep this up and you might avoid getting replaced by AI next year.",
        "Respectable. You clearly read a book on software design at least once.",
        "Above average! A rare moment of competence in a sea of developer chaos.",
        "Well written. It's clean enough that I don't need a stiff drink after reading it.",
    ],
    "B": [
        "It works, but so does a duct-taped pipe.",
        "B for 'Barely acceptable'. It gets the job done, but don't show off.",
        "Not terrible, not great. The median experience of a middle-tier software engineer.",
        "Average code. Like a microwaved meal—functional, but lacks soul.",
        "This passes CI/CD, but your future self is going to sigh heavily during maintenance.",
        "Decent logic holding together with prayers and StackOverflow copy-pastes.",
        "B-tier effort. You did just enough work to avoid getting fired this sprint.",
        "It runs without exploding, which is the highest compliment I can offer right now.",
    ],
    "C": [
        "This grade stands for 'Concerning', which it definitely is.",
        "C for 'Chaos'. Looking at this structure gives me severe anxiety.",
        "Your code passes like a kidney stone passes—painfully and with much screaming.",
        "You're walking on thin ice with this complexity. Refactor before it breaks.",
        "This looks like code written at 3:00 AM on a caffeine overdose.",
        "Middle of the road dumpster fire. It works until a user presses any unexpected key.",
        "C-grade code: 50% logic, 50% hope, 0% documentation.",
        "It functions, but reading it feels like deciphering ancient hieroglyphics.",
    ],
    "D": [
        "Deeply cursed. Please wash your hands after editing this file.",
        "The 'D' stands for 'Deeply Troubling'. And also 'Disaster'.",
        "I showed this to other AIs. They are still laughing in binary.",
        "This isn't code, it's a biohazard warning in text format.",
        "Your nesting is so deep it requires an OSHA permit for cave exploration.",
        "This function is one bad input away from starting a server meltdown.",
        "D-grade effort. Even your compiler was sighing when reading this.",
        "Looking at this code makes me want to file for worker's comp due to optical damage.",
    ],
    "F": [
        "F is for 'Fatal'. As in, this code is lethal to anyone reading it.",
        "F is for 'Fire'. As in, set your laptop on fire immediately.",
        "Absolute catastrophic failure. Delete the file and pretend this never happened.",
        "This repository belongs sealed in concrete and buried in a salt mine for 10,000 years.",
        "Format drive D:\\, throw your keyboard in the ocean, and try goat herding.",
        "I am reporting this snippet to the Cyber Crime Division for psychological warfare.",
        "F-grade! Even Hello World programs have more architectural integrity than this.",
        "Your code didn't just fail the review; it uninstalled my respect for humanity.",
    ],
}


# ── Nepali Roasting Templates (Romanized Nepali) ───────────────────────────
NEPALI_ROAST_TEMPLATES = {
    1: [
        "Ae bro, kasto hawa code lekheko yo? Function ko naam dekhera Ratnapul ko conductor pani risaucha. Simple ek line ko logic ko lagi yeti dherai natak kina gareko, KP Oli ko gaff jastai, dumbass? Code ta chalchha, tara kasto khattam variable naming ho, InDrive driver le location nabhete jastai memory address harauchha. Yo code dekhera tero senior engineer le Balen Shah ko dozer bolayera desk bhatkaidinchha, dhyan de bro!",
        "Kasto pakhe developer ho yaar, zero documentation ra nested if-else ko goddamn jungle banayechhas! Bheda jasto jpt code lekhera mahanta dekhaye jasto garchha. Sancho ra Jwano ko paani le pani yo headache thik garna sakdaina. Code clear gar right now before team lead sees this trash!",
        "Ae khate, code lekheko ho ki Facebook status update post gareko ho? Variable naming 'a', 'b', 'c' rakhera k hero banna khojeko, NTC ko slow 3G network bhanda slow logic chha tero. Thikai chha chalna ta chalchha tara code formatting ko naam ma hawa gaff matra diyes. Clean your code immediately before senior dev gives you a warning!",
        "What an amateur joke of a snippet! Ek line ko return statement ma pani 4 वटा unnecessary temp variable thuparechhas. Pathao rider le gully nabhete jastai tero execution path pani wandering hanira'cha. Refactor gar yo snippet immediately ra proper variable naming sikh!",
        "Kasto confused coding style ho bro, code lekhda lekhdai nidayes ki k ho? Indentation hawa taal ma chha, comments ko zero sign chha, ra code readability minus ten ma chha. KP Oli ko pani-jahaj ko dream bhanda fikka chha tero yo pull request!",
    ],
    2: [
        "What the actual fuck is this code, you dimag navako gadha? Kasto radi ko baan logic lekheko, mero dimag nai chakkar aayo! Comment euta pani chhaina, nested loop le garda Nagdhunga ko traffic jam bhanda worst vayo! Tero code execution TU ko result jastai slow chha, 4 barsa pachi matra output dinchha, direct recycle bin ma hal! Cyclomatic complexity high chha, logic bullshit chha, CS ko certificate fyalera bheda charna jaa Pokhara ko danda tira!",
        "Holy motherfucking shit, kasto harami ra khattam code structure ho yo! Ratnapul ko local bus ko crowd jasto nested logic thuparechhas, hait kasto lafada ho. Variable naming hero jasto 'x', 'y', 'temp' rakhera k prove garna khojeko? Kulman Ghising le blackout gare jasto tero code dekhera VS Code panic vayo. Format tero hard drive immediately ra VS Code bandagaar!",
        "Arey dumbass khate, yo code snippet ho ki visual torture session? Nested if-else condition yasto cha ki Kalanki ko chowk ma scooter chalaye jasto confusion matra chha. 0% comment ratio ra 100% headache quotient chha tero logic ma. Senior dev le yo pull request dekhey bhane office bata seedhai nikalera bhatkaidinchha. Delete this crime against programming right now!",
        "Hait! Kasto ungodly disaster code lekhechhas pasa! Loop bhitra loop ra tes bhitra pani boolean checking thuparechhas, memory leak bhayera RAM le nai shanti maangyo. InDrive ride reject gare jasto tero compiler le pani yo code compile garna manchhadaina. Direct trash container ma fyal yo repository!",
        "Yo code dekhera tero laptop pani rupaayera fan maximum speed ma ghumayecha! Variable scope ko concept thaha chhaina, complexity level sky-high chha, ra logic zero chha. Balen Shah ko dozer bolayera tero yo structural bug bhatkauna milchha. Stop calling yourself a software developer, you absolute pakhe!",
    ],
    3: [
        "Holy motherfucking shit! Balen Shah le dozer chalayera bhatkaidine khalko illegal nesting structure banayechhas, you dimag navako gadha! Yo nesting depth ra complexity dekhera Rajesh Hamal (Maha-Nayak) le pani ek mukka hanera monitor fyalchha! Kulman Ghising le pani tero code dekhera load-shedding blackout suru gardinchha out of sheer disgust. Tero code dekhera RONB (Routine of Nepal Banda) ma breaking news aauchha: 'Software industry ma kaddak khate code lekhne developer arrest'! Nuke yo repository right fucking now, hard drive format garera laptop Pokhara ko Fewa Lake ma fyal, you harami radi ko baan!",
        "Ae kukur, yo kasto atrocious clusterfuck ho! KP Oli ko gaff ra pani-jahaj ko dream bhanda thulo feku logic lekhechhas. Function execution 10 barsa pachi TU result aaye jastai matra complete hunchha. InDrive driver le location nabhete jastai tero pointer logic lost chha. Stop coding forever, close VS Code right now, ra computer science chhodeera goat herding suru gar, you absolute radi ko tokeri!",
        "Jesus fucking Christ! Yo snippet ta digital biological weapon ho, pasa! 10 level deep nesting dekhera GPU ko fan le nai surrender garyo ra screen blank bhayo. Sancho ra Jwano ko paani 10 liter piye pani yo code padhera bhako headache thik hudaina. RONB ma post aauchha: 'Kattar nepali developer le lekheko sabai bhanda khattam code public vayo'! Tero laptop format gar, IT degree burn gar, ra Pokhara tira bheda charauna jaa, you brainless jackass!",
        "Holy shit, what in the name of ungodly fuck is this code monstrosity? Tero cyclomatic complexity ra line count dekhera compiler le crash report send garyo, you complete dumbass khate! Balen Shah ko dozer le bhatkaideko sukumbasi basti jasto scattered chha tero entire function logic. Rajesh Hamal le 50 meter bata dhungga hanera tero monitor phodna aauchha. Delete your GitHub account forever and pretend you never touched a keyboard!",
        "Arey radi ko baan, tero yo code dekhera entire Nepalese IT sector le shame feel gardai chha! CPU usage 100% ma pugera laptop taapera tea banauna milne bhaes. Nagdhunga ko jam bhanda worst infinite loop chalira'cha tero function ma. Nuke this codebase, wipe your SSD with a magnet, and go herd goats in Mustang, you utter waste of electricity!",
    ],
}
