# trustra/reporter.py
import plotly.express as px
import plotly.io as pio
from jinja2 import Environment, BaseLoader

class TrustReport:
    def __init__(self, issues, cv_score, model_type, task, fairness_report=None):
        self.issues = issues
        self.cv_score = cv_score
        self.model_type = model_type
        self.task = task
        self.fairness_report = fairness_report

    def generate(self):
        fig = px.bar(x=["CV AUC"], y=[self.cv_score], title="Model Performance")
        plot_html = pio.to_html(fig, full_html=False)

        template = """
        <html><body>
        <h1>🛡️ TrustRA Trust Report</h1>
        <h2>Task: {{ task }} | Model: {{ model_type }} | CV AUC: {{ "%.3f" % cv_score }}</h2>

        <h3>⚠️ Issues Detected ({{ issues|length }})</h3>
        <ul>{% for issue in issues %}<li>{{ issue }}</li>{% endfor %}</ul>

        <h3>📊 Performance</h3>
        {{ plot|safe }}

        <h3>⚖️ Fairness Audit</h3>
        {% if fairness_report %}
          <ul>{% for k, v in fairness_report.items() %}
            <li><b>{{ k }}</b>: DPD={{ "%.3f" % v.DPD }}, EOD={{ "%.3f" % v.EOD }}</li>
          {% endfor %}</ul>
        {% else %}
          <p>No fairness audit performed.</p>
        {% endif %}

        </body></html>
        """

        html = Environment(loader=BaseLoader()).from_string(template).render(
            issues=self.issues,
            cv_score=self.cv_score,
            model_type=self.model_type,
            task=self.task,
            plot=plot_html,
            fairness_report=self.fairness_report
        )

        path = "trustra_report.html"
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        return path