from datetime import datetime

def calculate_phase(start_date: datetime):
    days_passed = (datetime.utcnow() - start_date).days + 1
    days_passed = min(max(days_passed, 1), 180)

    if days_passed <= 30:
        phase = "Phase 1: Foundation (A2 → B1)"
    elif days_passed <= 60:
        phase = "Phase 2: Intermediate Push (B1 → B1+)"
    elif days_passed <= 90:
        phase = "Phase 3: IELTS Transition (B2)"
    elif days_passed <= 120:
        phase = "Phase 4: Band 7.0 Push"
    elif days_passed <= 150:
        phase = "Phase 5: Band 7.5 Attack"
    else:
        phase = "Phase 6: Exam Simulation Mode"

    return days_passed, phase
