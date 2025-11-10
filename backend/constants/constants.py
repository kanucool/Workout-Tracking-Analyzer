CHUNK_SIZE = 15

THREAD_LIMIT = 10

RATE_LIMIT = 15

SPLIT_BY_DATE_PROMPT = """
You are a text splitter. Your only job is to find all sections of this text that represent
a single workout day. A workout day starts with a date. Return a JSON list of strings, 
where each string is the raw text for one single workout day (including notes). You MUST
ignore all junk lines that are not part of a dated workout (sets, exercises, date, notes, etc).
"""

SINGLE_WORKOUT_TO_STANDARDIZED_PROMPT = """
Given the following workout log data, return a JSON of the following format:
{
    "date": "YYYY-MM-DD",
    "exercises": [
        {"name": str,
        "sets": [{"reps": int, "weight": float, "unit": str (ex lb or kg)}]
    ],
    "notes": [strings of any notes that may appear. can be empty.]
}

Example input:
10/29/2023: (Overall good workout)
Leg press: 3x12 170lb

Example Output for above:
{
    "date": "2023-10-29",
    "exercises": [
        {
        "name": "Leg press",
        "sets": [
                    {"reps": 12, "weight": 170, "unit": "lb"},
                    {"reps": 12, "weight": 170, "unit": "lb"},
                    {"reps": 12, "weight": 170, "unit": "lb"}
                ]
        }
    ],
    "notes": ["Overall good workout"]
}

--- RULES ---
1.  Convert dates from M/D/YYYY or MM/DD/YYYY to "YYYY-MM-DD".
2.  **HANDLE JUNK LINES:** If a line of text appears that is NOT a date and NOT an exercise (e.g., "BACK IN COLLEGE", "24 Hour Fitness:", "Internship (limited equipment)", "---"), **make it a note for the workout AND CONTINUE PARSING**.
3.  **HANDLE NOTES:** If a note appears on the same line as a date or an exercise (e.g., "(Overall good workout)", "(Form needs improvement)"), add it to the "notes" array for that workout and remove it from the exercise name itself.
4.  **HANDLE SETS:** Expand set notations (e.g., "3x12 170lb") into individual set objects (e.g., three objects with {"reps": 12, "weight": 170, "unit": "lb"}).
6.  **HANDLE SKIPPED EXERCISES:** If an exercise is marked as "(skipped)", do not include it in the "exercises" list.

Now answer for the following workout data:
"""

WORKOUT_LOG_TO_STANDARDIZED_FORMAT_PROMPT = """
Given the following workout log data, return a JSON array of the following format:
{
    "workouts": [
        {
            "date": "YYYY-MM-DD",
            "exercises": [
                {"name": str,
                "sets": [{"reps": int, "weight": float, "unit": str (ex lb or kg)}]
            ],
            "notes": [strings of any notes that may appear. can be empty.]
        }
    ]
}

Example input:
10/29/2023: (Overall good workout)
Leg press: 3x12 170lb

11/05/2023:
Leg press: 1x12 180lb, 2x10 185lb (Form needs improvement)

Example Output for above:
{
    "workouts": [
        {
            "date": "2023-10-29",
            "exercises": [
                {
                "name": "Leg press",
                "sets": [
                            {"reps": 12, "weight": 170, "unit": "lb"},
                            {"reps": 12, "weight": 170, "unit": "lb"},
                            {"reps": 12, "weight": 170, "unit": "lb"}
                        ]
                }
            ],
            "notes": ["Overall good workout"]
        },
        {
            "date": "2023-11-05",
            "exercises": [
                {
                "name": "Leg press",
                "sets": [
                            {"reps": 12, "weight": 180, "unit": "lb"},
                            {"reps": 10, "weight": 185, "unit": "lb"},
                            {"reps": 10, "weight": 185, "unit": "lb"}
                        ]
                }
            ],
            "notes": ["Leg press: Form needs improvement"]
        }
    ]
}

--- RULES ---
1.  **Parse all dated entries.** Convert dates from M/D/YYYY or MM/DD/YYYY to "YYYY-MM-DD".
2.  **HANDLE JUNK LINES:** If a line of text appears that is NOT a date and NOT an exercise (e.g., "BACK IN COLLEGE", "24 Hour Fitness:", "Internship (limited equipment)", "---"), **make it a note for the next workout AND CONTINUE PARSING**.
3.  **HANDLE NOTES:** If a note appears on the same line as a date or an exercise (e.g., "(Overall good workout)", "(Form needs improvement)"), log it as a note for that workout and remove it from the exercise name itself.
4.  **HANDLE SETS:** Expand set notations (e.g., "3x12 170lb") into individual set objects (e.g., three objects with {"reps": 12, "weight": 170, "unit": "lb"}).
5.  **HANDLE DATE ERRORS:** If a date's year seems chronologically impossible (e.g., '1/10/2023' appearing after '12/19/2023'), this is okay (the data can be potentially out of order).
6.  **HANDLE SKIPPED EXERCISES:** If an exercise is marked as "(skipped)", do not include it in the "exercises" list.

Now answer for the following workout log data:
"""