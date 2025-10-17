import matplotlib.pyplot as plt
import io
import base64
from database.repositories import QuizRepository

# для вывода графика результата в сайте

class ResultsService:
    @staticmethod
    def generate_results_chart(results_data: dict) -> str:
        plt.style.use('default')
        fig, ax = plt.subplots(figsize=(10, 6))

        types = ['A', 'B', 'C', 'D']
        counts = [results_data.get('A', 0), results_data.get('B', 0),
                  results_data.get('C', 0), results_data.get('D', 0)]
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4']

        bars = ax.bar(types, counts, color=colors,
                      edgecolor='black', linewidth=2, alpha=0.8)

        for bar, count in zip(bars, counts):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'{count}', ha='center', va='bottom', fontsize=14, fontweight='bold')

        ax.set_ylabel('Количество ответов', fontsize=12, fontweight='bold')
        ax.set_xlabel('Типы личности', fontsize=12, fontweight='bold')
        ax.set_title('Результаты опросника', fontsize=16, fontweight='bold', pad=20)
        ax.set_ylim(0, max(counts) + 2)

        ax.grid(axis='y', alpha=0.3, linestyle='--')
        ax.set_axisbelow(True)

        for spine in ax.spines.values():
            spine.set_visible(False)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100, bbox_inches='tight',
                    facecolor='white', edgecolor='none')
        plt.close(fig)
        buf.seek(0)

        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return f"data:image/png;base64,{image_base64}"

    @staticmethod
    def get_user_results(user_id: int):
        result = QuizRepository.get_latest_results(user_id)
        if result and result[1]:
            results_data = eval(result[1])
            chart_image = ResultsService.generate_results_chart(results_data)
            return {
                "results": results_data,
                "image": chart_image
            }
        return None