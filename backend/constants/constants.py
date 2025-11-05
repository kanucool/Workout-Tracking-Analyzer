BASE_PROMPT = """
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

If some data is missing, extrapolate and make assumptions to fill in the blanks.
If the number of sets for an exercise is unusually high (think 50+ sets for one
exercise in a single workout), exclude it from the output.
If a note appears next to an exercise name, exclude it from the name of the exercise,
and include it in the notes section instead.
Now answer for the following workout log data:
"""