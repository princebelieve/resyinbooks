from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
SOURCES = PROJECT / "Professor_Supplied"
OUTPUT = HERE / "WAEC_NECO_English_Language_Revision_Handbook_Assembly_Draft.md"

parts = [
    "# The Complete WAEC/NECO English Language Revision Handbook\n\n"
    "**Prof. Johnson Agharese Egonmwan**\n\n"
    "*Editorial assembly draft — not a final proof*\n\n"
    "---\n\n",
    (HERE / "Chapter_01_Introduction_to_English_Language_Draft.md").read_text(
        encoding="utf-8"
    ),
]

for number, filename in [
    (2, "Chapter_02_Grammar_Parts_of_Speech.txt"),
    (3, "Chapter_03_Tenses_and_Sentence_Structure.txt"),
    (4, "Chapter_04_Concord.txt"),
    (5, "Chapter_05_Lexis_and_Structure.txt"),
    (6, "Chapter_06_Comprehension.txt"),
    (7, "Chapter_07_Summary_Writing.txt"),
    (8, "Chapter_08_Essay_Writing.txt"),
    (9, "Chapter_09_Letter_Writing.txt"),
    (10, "Chapter_10_Oral_English.txt"),
    (11, "Chapter_11_Figures_of_Speech_and_Literary_Devices.txt"),
    (12, "Chapter_12_Registers_and_Idioms.txt"),
    (13, "Chapter_13_Vocabulary_Development.txt"),
    (14, "Chapter_14_WAEC_NECO_Practice.txt"),
    (15, "Chapter_15_Mock_Examinations_and_Marking_Guide.txt"),
    (16, "Chapter_16_Examination_Success_and_Communication.txt"),
]:
    if number == 15:
        text = (HERE / "Chapter_15_Complete_Mock_Examinations_Draft.md").read_text(
            encoding="utf-8"
        ).strip()
    else:
        source = SOURCES / filename
        text = source.read_text(encoding="utf-8-sig").strip()
    if number == 14:
        text = text.replace(
            "Time Allowed: 2 hours 30 minutes.\n\n"
            "Instruction: Attempt all objective questions and all compulsory theory questions.",
            "Use this checklist as mixed revision practice. Follow the current official "
            "paper instructions for your examination series; this handbook exercise "
            "does not set an official duration or compulsory-section pattern.",
        )
    if number == 16:
        text = text.replace(
            "For a paper lasting about 2 hours 30 minutes:\n\n"
            "Section| Suggested Time\n"
            "Objective Questions| 45 minutes\n"
            "Essay Writing| 50 minutes\n"
            "Comprehension| 25 minutes\n"
            "Summary| 20 minutes\n"
            "Revision of Answers| 10 minutes\n\n"
            "Always wear a wristwatch where examination regulations permit and monitor your progress.",
            "Paper duration and section timing vary by examination body and series. "
            "Read the instructions on your question paper, divide the available time "
            "among the required tasks, and leave a short period to review your answers. "
            "Use a timepiece only where the examination rules permit it.",
        )
    parts.append(f"\n\n---\n\n{text}\n")

OUTPUT.write_text("".join(parts), encoding="utf-8", newline="\n")
print(f"Wrote {OUTPUT}")
