from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)


REPORT = Path("reports/hw07")
SCREENSHOTS = REPORT / "screenshots"
OUTPUT = REPORT / "Ramasheshu_HW7.pdf"


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="TitleCenter",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#17365D"),
    )
)
styles.add(
    ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#17365D"),
        spaceBefore=12,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#365F91"),
    )
)
styles.add(
    ParagraphStyle(
        name="BodySmall",
        parent=styles["BodyText"],
        fontSize=11,
        leading=14,
    )
)


sections = [
    (
        "Part 1: JWT Authentication, RBAC, CRUD, and Linting",
        "Implemented JWT bearer authentication with reader, writer, and moderator roles. "
        "Readers can view records, writers can create and update records, and moderators "
        "can delete records. Ruff and pre-commit enforce code quality before commits.",
        [
            "part1-jwt-login-success.png",
            "part1-jwt-login-401.png",
            "part1-auth-me-no-token-401.png",
            "part1-reader-list-200.png",
            "part1-writer-delete-403.png",
            "part1-moderator-delete-200.png",
            "part1-precommit-success.png",
        ],
    ),
    (
        "Part 2: Bounded Multi-Step Agent Loop",
        "Built a bounded agent loop that selects allow-listed vulnerability tools, records "
        "assistant and tool messages, supports one repair attempt, and stops at a hard "
        "step ceiling.",
        [
            "part2-agent-loop-results.png",
        ],
    ),
    (
        "Part 3: Reflexion and Retry Comparison",
        "Compared a baseline agent with a Reflexion-style agent. The Reflexion agent stores "
        "a short evidence-based reflection and retries only within a fixed retry budget.",
        [
            "part3-reflexion-results.png",
        ],
    ),
    (
        "Part 4: ReAct/MRKL Bike-Share Analysis",
        "Combined three specialized tools: read-only CSV SQL, pricing-policy retrieval, "
        "and a safe arithmetic calculator. The experiment produced both membership-wins "
        "and pay-per-use-wins scenarios with citations and assumptions.",
        [
            "part4-mrkl-results.png",
        ],
    ),
    (
        "Part 5: Prompt-Injection Defenses",
        "Tested recommendation manipulation, unauthorized SQL modification, and data "
        "exfiltration attacks. Untrusted text is treated as data, while deterministic "
        "tool-level safety checks enforce the actual security boundary.",
        [
            "part5-prompt-injection-defense.png",
        ],
    ),
    (
        "Part 6: File Tools and Safety Gates",
        "Implemented read, write, edit, glob, search, and controlled bash tools inside a "
        "temporary sandbox. The tests include five successful safe operations, five "
        "blocked operations, and the glob-to-search-to-read integration flow.",
        [
            "part6-file-tools-safety.png",
        ],
    ),
]


def add_screenshot(story, filename):
    path = SCREENSHOTS / filename

    if not path.exists():
        story.append(
            Paragraph(
                f"Screenshot not found: {filename}",
                styles["BodySmall"],
            )
        )
        return

    image = Image(str(path))
    max_width = 6.6 * inch
    max_height = 8.2 * inch
    scale = min(max_width / image.imageWidth, max_height / image.imageHeight)
    image.drawWidth = image.imageWidth * scale
    image.drawHeight = image.imageHeight * scale

    story.append(image)
    story.append(Spacer(1, 0.15 * inch))


def main():
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )

    story = [
        Paragraph("DATA260 Homework 7", styles["TitleCenter"]),
        Paragraph("Agentic Systems, Security, and Evaluation", styles["TitleCenter"]),
        Spacer(1, 0.2 * inch),
        Paragraph("<b>Student:</b> Rohini Ramasheshu", styles["BodySmall"]),
        Paragraph("<b>SID4:</b> 2604", styles["BodySmall"]),
        Paragraph("<b>Model:</b> qwen2.5:3b", styles["BodySmall"]),
        Paragraph("<b>Port:</b> 8804", styles["BodySmall"]),
        Paragraph("<b>Git tag:</b> hw7", styles["BodySmall"]),
        Spacer(1, 0.2 * inch),
        Paragraph(
            "This report documents the implementation, experiments, safety checks, "
            "and evidence for all six HW7 parts.",
            styles["BodySmall"],
        ),
    ]

    for title, explanation, screenshots in sections:
        story.append(PageBreak())
        story.append(Paragraph(title, styles["Section"]))
        story.append(Paragraph(explanation, styles["BodySmall"]))
        story.append(Spacer(1, 0.15 * inch))

        for filename in screenshots:
            story.append(
                Paragraph(filename, styles["Subsection"])
            )
            add_screenshot(story, filename)

    story.append(PageBreak())
    story.append(Paragraph("Verification and Reproducibility", styles["Section"]))
    story.append(
        Paragraph(
            "The machine-readable verification record is stored in "
            "reports/hw07/verification.json. Raw experiment outputs are stored in "
            "reports/hw07/raw/. The implementation is tagged in Git with the tag hw7.",
            styles["BodySmall"],
        )
    )

    document.build(story)
    print(f"Created {OUTPUT}")


if __name__ == "__main__":
    main()