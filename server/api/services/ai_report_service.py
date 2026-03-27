try:
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_groq import ChatGroq
except ImportError:
    ChatGroq = None

from api.models import StudentMark, StudentResult


class AIReportService:
    def __init__(self, api_key):
        self.api_key = api_key
        if ChatGroq:
            self.llm = ChatGroq(
                api_key=api_key,
                model_name="llama-3.3-70b-versatile",
                max_tokens=500,
            )
        else:
            self.llm = None

    def generate_report(self, student_result):
        try:
            if not self.llm:
                return None
            student = student_result.student
            exam = student_result.exam_type
            marks = StudentMark.objects.filter(student=student, exam_type=exam).select_related("subject")
            previous_result = (
                StudentResult.objects.filter(student=student, exam_type__class_name=exam.class_name)
                .exclude(id=student_result.id)
                .order_by("-exam_type__date")
                .first()
            )

            previous_percentage = previous_result.percentage if previous_result else None
            improvement = 0.0
            if previous_percentage is not None:
                improvement = student_result.percentage - previous_percentage

            marks_lines = "\n".join(
                [
                    f"- {mark.subject.name}: {mark.marks_obtained}/{mark.max_marks}"
                    for mark in marks
                ]
            )

            system_prompt = (
                "You are a school report card writer. Generate warm, encouraging, "
                "professional parent-facing reports in 3 paragraphs. Be specific about "
                "subjects. Never be harsh."
            )

            user_prompt = (
                f"Student Name: {student.name}\n"
                f"Class: {student.class_name}\n"
                f"Exam: {exam.name}\n"
                f"Subject-wise marks:\n{marks_lines}\n\n"
                f"Total: {student_result.total_marks}/{student_result.max_total}\n"
                f"Percentage: {student_result.percentage}%\n"
                f"Rank: {student_result.rank if student_result.rank else 'N/A'}\n"
                f"Previous exam percentage: {previous_percentage if previous_percentage is not None else 'N/A'}\n"
                f"Improvement: {improvement:.2f}%"
            )

            if not self.llm:
                return None

            system_msg = SystemMessage(content=system_prompt)
            human_msg = HumanMessage(content=user_prompt)

            response = self.llm.invoke([system_msg, human_msg])
            return response.content.strip()
        except Exception as e:
            print("Failed generating report:", e)
            return None
