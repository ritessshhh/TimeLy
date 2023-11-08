import openai
import pandas as pd


class CourseRecommender:
    def __init__(self, dataset_path):
        self.data = pd.read_excel(dataset_path)
        self.difficulties = self.calculate_difficulty()

    def calculate_difficulty(self):
        grouped_courses = self.data.groupby("Course")
        difficulties = {}

        # Handle possible NaN values
        self.data.fillna(0, inplace=True)

        for course, course_data in grouped_courses:
            total_students = course_data[['A', 'B', 'B+', 'B-', 'C', 'C+', 'C-', 'D+', 'D', 'F']].sum(axis=1).sum()
            total_A = course_data['A'].sum()

            # Ensure total_students is not zero
            if total_students == 0:
                difficulty = 0
            else:
                difficulty = (total_students - total_A) / total_students

            difficulties[course] = difficulty

        return difficulties

    def recommend_course(self, preference):
        sorted_difficulties = sorted(self.difficulties.items(), key=lambda x: x[1])

        if preference == "easy":
            recommended_course, _ = sorted_difficulties[0]
        elif preference == "hard":
            recommended_course, _ = sorted_difficulties[-1]
        elif preference == "medium":
            mid_index = len(sorted_difficulties) // 2
            recommended_course, _ = sorted_difficulties[mid_index]
        else:
            return "Invalid preference provided!"

        # Get the associated section(s) for the recommended course
        sections = self.data[self.data["Course"] == recommended_course]["Section"].unique()
        sections_str = ", ".join(sections)

        return f"{recommended_course} (Section: {sections_str})"

    def assist(self, user_input, conversation_history=[]):
        messages = conversation_history + [{"role": "user", "content": user_input}]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        return response.choices[0].message['content']


# Ensure you've set the OpenAI API key correctly
openai.api_key = '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'

recommender = CourseRecommender("MergedFile.xlsx")

conversation_history = []
while True:
    user_input = input("You: ")
    if user_input.lower() in ['exit', 'quit']:
        break
    response = recommender.assist(user_input, conversation_history)
    conversation_history.append({"role": "user", "content": user_input})
    conversation_history.append({"role": "system", "content": response})
    print("CourseRecommender:", response)
