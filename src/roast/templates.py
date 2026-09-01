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

    # ── Easter Egg: Hello World ──────────────────────────────────────────
    "easter_hello_world": [
        "A 'Hello World' program. Congratulations on solving the coding challenge that literally every tutorial starts with. You must be so proud.",
        "You submitted a Hello World. This is the programming equivalent of showing up to a marathon and just stretching at the starting line.",
        "Hello World? That's it? I have more complex logic in my sleep mode. Even my error handler has more depth than this.",
        "Ah, Hello World — the classic 'I installed Python 30 seconds ago' flex. Bold of you to submit this to a code analyzer.",
        "You wrote Hello World and asked me to review it. This is like asking Gordon Ramsay to critique a glass of tap water.",
        "Hello World. The coding equivalent of a participation trophy. Thanks for showing up, I guess.",
        "Submitting Hello World to CodeRoast is like bringing a butter knife to a sword fight. Adorably pointless.",
        "Even ChatGPT would be offended if you asked it to review this. Hello World. Two words. Zero effort. Peak developer energy.",
    ],

    # ── Easter Egg: FizzBuzz ─────────────────────────────────────────────
    "easter_fizzbuzz": [
        "FizzBuzz! Congratulations on solving the interview question that filters out 50% of candidates. You are now qualified to breathe near a codebase.",
        "Ah, FizzBuzz — the developer's rite of passage. You've proven you understand modulo. Your parents must be thrilled.",
        "You submitted FizzBuzz to a code analyzer. This is the software engineering equivalent of asking a teacher to grade your ABCs in college.",
        "FizzBuzz detected. I'd roast this, but honestly it's already the punchline to every coding interview joke ever told.",
        "Classic FizzBuzz. The only algorithm where even the solution feels like an insult to computer science.",
        "FizzBuzz? Next you'll ask me to review your 'for i in range(10): print(i)' masterpiece. Dream bigger.",
    ],

    # ── Easter Egg: Empty/Minimal Code ───────────────────────────────────
    "easter_empty": [
        "You submitted nothing. Technically, this is the cleanest code I've ever seen. Zero bugs. Zero complexity. Zero value.",
        "An empty file. The most efficient code ever written — does absolutely nothing, perfectly. Ship it to production.",
        "Nothing. You gave me nothing. This is the developer equivalent of handing in a blank exam paper and walking out.",
        "Empty code submitted. This has fewer bugs than 99% of production codebases. You've peaked. Retire now.",
        "You submitted an empty snippet. I have more content in my loading screen than your entire contribution.",
        "Blank code. Truly a masterpiece of minimalism. Somewhere, a Silicon Valley startup is calling this 'disruptive architecture'.",
    ],

    # ── Easter Egg: TODO/Pass Stubs ──────────────────────────────────────
    "easter_todo": [
        "Your code is 90% TODO comments and 10% pass statements. Bold strategy — outsource the actual work to your future self.",
        "I found more TODO comments than actual code. This isn't a program, it's a procrastination manifesto.",
        "def do_something(): pass. def main(): pass. This isn't code, it's a developer's draft of their resignation letter.",
        "You wrote 'TODO: implement later' six times. Later never comes. We both know this. Your IDE knows this.",
        "Your code has more 'pass' statements than a basketball game. At least basketball players eventually score.",
    ],
}



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
        "Arey pasa, yo code padhda padhdai mero battery percent 100% bata 5% ma jhyap bhayo! Simple validation check garnu parne ma yeti dherai unwanted code lines kina lekheko? Format your code properly, zero documentation ra zero effort chha!",
        "What a hawa attempt at programming! Function parameter ko type declaration chhaina, error handling vanish bhayeko chha. Senior dev le yo commit dekhyo bhane tero laptop ko power cord nai kater fyalchha. Clean it up right now!",
        "Ae bheda, yo snippet ma logic bhanda dherai spaces ra empty lines matra dekhinchha! Kasto lazy habit ho yo, code formatting extension install garna pani alas lagchha ki k ho? Direct refactor gar or suffer the consequences!",
        "Yo logic dekhera Lagankhel-Ratnapul local bus ko jam ko yaad aayo! Unstructured coding style, zero variable safety, ra 100% hawa implementation. Improve your code before pushing to main branch, dumbass!",
        "Broski, yo code dekhera tero computer teacher le pani certificate firta maangchha! Simple loop chalauna pani yeti dherai unwanted temporary arrays thuparechhas. Clean gar yo mess immediately!",
    ],
    2: [
        "What the actual fuck is this code, you dimag navako gadha? Kasto hawa ra khattam logic lekheko, mero dimag nai chakkar aayo! Comment euta pani chhaina, nested loop le garda Nagdhunga ko traffic jam bhanda worst vayo! Tero code execution TU ko result jastai slow chha, 4 barsa pachi matra output dinchha, direct recycle bin ma hal! Cyclomatic complexity high chha, logic bullshit chha, CS ko certificate fyalera bheda charna jaa Pokhara ko danda tira!",
        "Holy motherfucking shit, kasto harami ra khattam code structure ho yo! Ratnapul ko local bus ko crowd jasto nested logic thuparechhas, hait kasto lafada ho. Variable naming hero jasto 'x', 'y', 'temp' rakhera k prove garna khojeko? Kulman Ghising le blackout gare jasto tero code dekhera VS Code panic vayo. Format tero hard drive immediately ra VS Code bandagaar!",
        "Arey dumbass khate, yo code snippet ho ki visual torture session? Nested if-else condition yasto cha ki Kalanki ko chowk ma scooter chalaye jasto confusion matra chha. 0% comment ratio ra 100% headache quotient chha tero logic ma. Senior dev le yo pull request dekhey bhane office bata seedhai nikalera bhatkaidinchha. Delete this crime against programming right now!",
        "Hait! Kasto ungodly disaster code lekhechhas pasa! Loop bhitra loop ra tes bhitra pani boolean checking thuparechhas, memory leak bhayera RAM le nai shanti maangyo. InDrive ride reject gare jasto tero compiler le pani yo code compile garna manchhadaina. Direct trash container ma fyal yo repository!",
        "Yo code dekhera tero laptop pani rupaayera fan maximum speed ma ghumayecha! Variable scope ko concept thaha chhaina, complexity level sky-high chha, ra logic zero chha. Balen Shah ko dozer bolayera tero yo structural bug bhatkauna milchha. Stop calling yourself a software developer, you absolute pakhe!",
        "Ae khate dimag navako, yo kasto spaghetti logic lekheko ho! Recursive call bhitra base condition narakhera stack overflow vayo. Pathao rider le wrong location ma puraye jastai tero code le wrong memory write gareko chha. Nuke this function and rewrite from scratch!",
        "What a clusterfuck of a code snippet, pasa! Nesting depth 4 bhanda mathi pugyo, variable name sabai random alphabet letters chha. KP Oli le gaff diye jasto tero code le execution ko feyku promises matra garira'cha. Delete gar yo disaster right now!",
        "Yo function padhda padhdai mero 2 barsa ko aayush ghatyo, you dumbass! Duplicate logic le garda maintenance nightmare banisakechhas. Sancho lagaye pani yo code le dieko headache thik hudaina. Clean up your architecture right fucking now!",
        "Arey bheda, yo code lekhna lai kasto weed ganja taneko thiyes? Exception handling zero chha, null pointer exception le app crash hunchha. Balen Shah le sadak ko illegal ghar bhatkaye jastai tero code base bhatkauna parchha. Refactor immediately!",
        "Kasto atrociously terrible logic ho yo! Hardcoded API key ra credentials commit garira'cha, security risk level maximum ma chha. RONB ma post aauchha tero security flaw ko barema! Wipe this repo right now, you careless idiot!",
    ],
    3: [
        "Holy motherfucking shit! Balen Shah le dozer chalayera bhatkaidine khalko illegal nesting structure banayechhas, you dimag navako gadha! Yo nesting depth ra complexity dekhera Rajesh Hamal (Maha-Nayak) le pani ek mukka hanera monitor fyalchha! Kulman Ghising le pani tero code dekhera load-shedding blackout suru gardinchha out of sheer disgust. Tero code dekhera RONB (Routine of Nepal Banda) ma breaking news aauchha: 'Software industry ma kaddak khate code lekhne developer arrest'! Nuke yo repository right fucking now, hard drive format garera laptop Pokhara ko Fewa Lake ma fyal, you pakhe harami!",
        "Ae kukur, yo kasto atrocious clusterfuck ho! KP Oli ko gaff ra pani-jahaj ko dream bhanda thulo feku logic lekhechhas. Function execution 10 barsa pachi TU result aaye jastai matra complete hunchha. InDrive driver le location nabhete jastai tero pointer logic lost chha. Stop coding forever, close VS Code right now, ra computer science chhodeera goat herding suru gar, you absolute dimag navako gadha!",
        "Jesus fucking Christ! Yo snippet ta digital biological weapon ho, pasa! 10 level deep nesting dekhera GPU ko fan le nai surrender garyo ra screen blank bhayo. Sancho ra Jwano ko paani 10 liter piye pani yo code padhera bhako headache thik hudaina. RONB ma post aauchha: 'Kattar nepali developer le lekheko sabai bhanda khattam code public vayo'! Tero laptop format gar, IT degree burn gar, ra Pokhara tira bheda charauna jaa, you brainless jackass!",
        "Holy shit, what in the name of ungodly fuck is this code monstrosity? Tero cyclomatic complexity ra line count dekhera compiler le crash report send garyo, you complete dumbass khate! Balen Shah ko dozer le bhatkaideko sukumbasi basti jasto scattered chha tero entire function logic. Rajesh Hamal le 50 meter bata dhungga hanera tero monitor phodna aauchha. Delete your GitHub account forever and pretend you never touched a keyboard!",
        "Arey dimag navako gadha, tero yo code dekhera entire Nepalese IT sector le shame feel gardai chha! CPU usage 100% ma pugera laptop taapera tea banauna milne bhaes. Nagdhunga ko jam bhanda worst infinite loop chalira'cha tero function ma. Nuke this codebase, wipe your SSD with a magnet, and go herd goats in Mustang, you utter waste of electricity!",
        "Ae harami kukur, tero yo code dekhera entire Kathmandu Valley ko power grid crash vayo! Infinite recursion, zero memory management, ra 10 level deep nested loop le garda Kulman Ghising le pani tero ghar ko line kaatidinchha. Format tero PC, throw your keyboard into Trisuli river, ra bheda charna jaa, you brainless idiot!",
        "What an absolute abominable atrocity! Tero code architecture dekhera CPU le thermal throttling garera shutdown handyo. Rajesh Hamal (Maha-Nayak) le 100 meter bata dhungga fyalera tero screen phodchha if you don't delete this repository. Shut down VS Code forever, you dimag navako pakhe!",
        "Hait! Yo code lekhne developer lai Nepal Rastra Bank ko cyber crime branch ma hand over garnu parchha! Security vulnerabilities everywhere, hardcoded secrets, ra absolute garbage logic. RONB ma breaking news: 'Worst Nepalese code of the decade discovered'! Burn your laptop, you ungodly khate!",
        "Arey dumbass, tero yo logic dekhera Fewa Lake ko paani pani tatauchha out of sheer anger! Cyclomatic complexity infinity ma pugera compiler melted down. Balen Shah le dozer chalayera tero home folder nai erase gardinchha. Stop touching computers forever, you absolute useless piece of shit!",
        "Jesus Christ, yo snippet padhera mero brain cell million wota dead vayo! Infinite memory leak, undefined variable references, ra total architectural disaster. Format drive D:\\, throw your laptop into Karnali river, and go herd Yaks in Manang, you hopeless dimag navako gadha!",
        "Holy fucking mother of disasters! Tero code dekhera Harke Sampang le Dharan ma dhungga boke jastai tero RAM ra CPU le yo logic run garna dhungga bokna parya chha, you dimag navako gadha! Prakash Saput ko song 'Sakambhari' jastai dramatic crisis banaye'chhas function ma. 100kg gold scam bhanda thulo scam ho tero computer science degree. Delete gar yo clusterfuck immediately ra laptop fyal Bagmati ko fohor paani ma, you absolute pakhe khate!",
        "What the motherfucking unholy hell is this code, pasa! Bhaktapur ko JuJu Dhau jasto mitho hoina, Selroti jasto gol-gol infinite loop ma ghumera CPU taapera tea banauna milne vayo. Deuba le 'Arey bhai k bolya' bhane jastai tero compiler le k bolya thaha payena out of sheer confusion. Mukunda Ghimire le pani yo code padhera maanasik santulan gumayecha! Format tero drive D:\\ and go herd goats in Mustang, you ungodly khate!",
        "Ae dimag navako gadha, yo code ho ki Dasharath Rangasala ma bhakundo haney jasto ball stadium bahira gayo out of memory bounds! Bagmati ko fohor paani bhanda ganda ra toxic chha tero entire architecture. Everest bhanda thulo peak complexity banayechhas, local microbus conductor le 'Chauki chauki!' karaye jastai tero error handler crash vayo. Stop touching computers forever, burn your IT certificate, ra Pokhara ko Fewa Lake ma jump hande, you brainless gadha!",
        "Jesus fucking Christ! Yo snippet padhera Pashupatinath ko bhatbhatini ma pani shanti milne chhainna out of sheer torture! Hardcoded credentials, zero variable scope, ra nested loops ko mega catastrophe. 100kg gold scam ko investigation bhanda complex ra hopeless chha tero variable logic. Nuke this codebase with nuclear fire and go herd Yaks in Manang, you utter waste of human existence!",
        "Holy motherfucking disaster! Tero function ma logic chhaina, Samsad bhaban ko hawa halla ra fight bhanda worst chaos chha, pasa! Vten le rap spit gare jasto mero terminal le profanity spit garyo tero code dekhera. InDrive ride 10 choti cancel bhaye jastai compiler le 10 choti crash report garyo. Delete your GitHub account right now, close your laptop, and never code again in this lifetime, you harami dimag navako gadha!",
        "Ae kukur dimag navako, yo kasto nuclear hazard level code lekheko ho! Achar navako jhol momo jasto dry, tasteless ra depressing chha tero code style. Tilicho Lake ko -20 degree cold water bhanda ni thanda freeze vayo tero CPU fan. RONB ma breaking news aauchha: 'Nepal ko sabai bhanda khattam developer le software industry ruin garyo'! Wipe your SSD with a neodymium magnet right now, you absolute waste of electricity!",
        "What in the name of ungodly fuck! Yo snippet padhera mera tin wota generation ko dimag kharab bhayo, you pakhe gadha! Balen Shah ko dozer le KMC ko illegal footpath bhatkaye jastai tero entire function hierarchy bhatkaidinchhu. 10 level deep nesting dekhera GPU ko VRAM le surrender handyo. Go herd goats in Humla Jumla, you hopeless dimag navako gadha!",
        "Arey dumbass, tero code execution ma yeti dherai latency chha ki Tribhuvan University ko exam result aaye pachi matra loop finish hunchha! KP Oli ko pani-jahaj ra gass pipeline ko gaff bhanda 100 times bigger feku logic ho yo. InDrive driver le offline janchhu bhane jastai tero server offline gayo! Nuke this repository right now before senior dev sues you for biological warfare!",
        "Holy shit! Yo code dekhera Rajesh Hamal (Maha-Nayak) le 200 meter bata dhungga hanera tero monitor ra laptop phodchha, pasa! Simple array iteration garna lai 15 wota temporary variables ra nested checks thuparechhas, hait kasto goddamn lafada ho! Format tero PC immediately and surrender your engineering degree to Kathmandu Metropolitan City!",
        "Ae khate, yo code ho ki Mukundaland ko manifesto? Zero readability, zero comments, ra 1000% headache quotient. Sajha bus ko crowd jasto packed nested if statements le garda VS Code auto-close bhayo. Delete your codebase, throw your laptop in Bagmati river, and go apply for a tourist guide job in Nagarkot, you useless piece of shit!",
        "Jesus Christ! Yo snippet ma memory safety bhanda dherai security holes chha, Kathmandu ko sadak ko khadde jastai! Harke Sampang le water pipe khoje jastai tero pointer logic le memory leak khojira'cha. Delete gar yo repository right now, RONB ma post auna bhanda agadi!",
        "What an absolute abominable clusterfuck! Tero cyclomatic complexity dekhera NASA ko supercomputer pani crash hunchha! KP Oli ko gaff jastai zero substance, pure noise. Hard drive format garera laptop Pokhara ko Fewa Lake ma fyal, you harami dimag navako gadha!",
        "Ae bheda, yo code dekhera tero entire software engineering batch le suicide note lekhchha! Exception handling zero, nesting sky high, ra code structure radioactive waste. Shut down VS Code forever, you dimag navako gadha!",
        "Arey dimag navako gadha, yo snippet padhera mero eye doctor le visual disability certificate diyo! 12 level deep nesting, zero comments, ra pure chaos. Delete your GitHub account immediately, you absolute failure of a developer!",
    ],
}
