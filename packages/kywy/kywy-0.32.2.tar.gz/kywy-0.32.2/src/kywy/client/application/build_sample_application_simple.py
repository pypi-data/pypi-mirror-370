import pandas as pd

from ...client.kawa_client import KawaClient
from ...client.kawa_decorators import kawa_tool

from datetime import datetime, date, timedelta
import pandas as pd
import numpy as np
from faker import Faker


def kawa():
    k = KawaClient(kawa_api_url='http://localhost:4200')
    k.set_api_key(api_key_file='/Users/emmanuel/doc/local-pristine/.key')
    k.set_active_workspace_id(workspace_id='79')
    return k


app = kawa().app(
    application_name='Health Insurance Underwriting Management III',
    sidebar_color='#2c5aa0',
)


# -- DATA SECTION: start

@kawa_tool(outputs={'application_id': str, 'applicant_name': str, 'age': float, 'gender': str, 'bmi': float,
                    'smoking_status': str, 'occupation': str, 'annual_income': float, 'medical_history': str,
                    'chronic_conditions': str, 'application_date': date, 'policy_type': str, 'coverage_amount': float,
                    'premium_quoted': float, 'underwriter_id': str})
def underwriting_applications_generator():
    fake = Faker()
    data = []
    genders = ['Male', 'Female']
    smoking_statuses = ['Never', 'Former', 'Current']
    occupations = ['Software Engineer', 'Teacher', 'Doctor', 'Nurse', 'Construction Worker', 'Sales Manager',
                   'Accountant', 'Police Officer', 'Firefighter', 'Pilot']
    medical_histories = ['None', 'Diabetes', 'Hypertension', 'Heart Disease', 'Cancer History', 'Asthma', 'Depression',
                         'Anxiety']
    chronic_conditions_c = ['None', 'Type 2 Diabetes', 'High Blood Pressure', 'Arthritis', 'COPD', 'Heart Failure']
    policy_types = ['Term Life', 'Whole Life', 'Critical Illness', 'Disability Insurance']
    underwriters = ['UW001', 'UW002', 'UW003', 'UW004', 'UW005']

    for i in range(250):
        application_id = f"APP{i + 1:05}"
        applicant_name = fake.name()
        age = np.random.normal(45, 15)
        age = max(18, min(80, age))
        gender = np.random.choice(genders)
        bmi = np.random.normal(26, 4)
        bmi = max(16, min(45, bmi))
        smoking_status = np.random.choice(smoking_statuses)
        occupation = np.random.choice(occupations)
        annual_income = np.random.lognormal(11, 0.5)
        medical_history = np.random.choice(medical_histories)
        chronic_conditions = np.random.choice(chronic_conditions_c)
        application_date = fake.date_between(start_date='-2y', end_date='today')
        policy_type = np.random.choice(policy_types)
        coverage_amount = np.random.choice([100000, 250000, 500000, 750000, 1000000])

        # Premium calculation based on risk factors
        base_premium = coverage_amount * 0.002
        age_factor = 1 + (age - 30) * 0.02
        bmi_factor = 1 + max(0, (bmi - 25) * 0.05)
        smoking_factor = 1.5 if smoking_status == 'Current' else 1.2 if smoking_status == 'Former' else 1.0
        occupation_factor = 1.3 if occupation in ['Police Officer', 'Firefighter', 'Pilot'] else 1.0
        medical_factor = 1.4 if medical_history != 'None' else 1.0

        premium_quoted = base_premium * age_factor * bmi_factor * smoking_factor * occupation_factor * medical_factor

        underwriter_id = np.random.choice(underwriters)

        data.append([application_id, applicant_name, age, gender, bmi, smoking_status, occupation, annual_income,
                     medical_history, chronic_conditions, application_date, policy_type, coverage_amount,
                     premium_quoted, underwriter_id])

    df = pd.DataFrame(data, columns=['application_id', 'applicant_name', 'age', 'gender', 'bmi', 'smoking_status',
                                     'occupation', 'annual_income', 'medical_history', 'chronic_conditions',
                                     'application_date', 'policy_type', 'coverage_amount', 'premium_quoted',
                                     'underwriter_id'])
    return df


@kawa_tool(
    outputs={'decision_id': str, 'application_id': str, 'decision_date': date, 'decision': str, 'risk_score': float,
             'final_premium': float, 'exclusions': str, 'notes': str, 'processing_days': float})
def underwriting_decisions_generator():
    fake = Faker()
    data = []
    decisions = ['Approved', 'Declined', 'Approved with Conditions', 'Pending Medical Exam']
    exclusions_list = ['None', 'Pre-existing Conditions', 'High-Risk Activities', 'Mental Health', 'Cancer Coverage']

    for i in range(220):
        decision_id = f"DEC{i + 1:05}"
        application_id = f"APP{i + 1:05}"
        decision_date = fake.date_between(start_date='-18m', end_date='today')
        decision = np.random.choice(decisions, p=[0.65, 0.15, 0.15, 0.05])
        risk_score = np.random.uniform(1, 10)
        final_premium = np.random.uniform(500, 15000)
        exclusions = np.random.choice(exclusions_list)
        notes = fake.sentence()
        processing_days = np.random.uniform(3, 30)

        data.append([decision_id, application_id, decision_date, decision, risk_score, final_premium, exclusions, notes,
                     processing_days])

    df = pd.DataFrame(data, columns=['decision_id', 'application_id', 'decision_date', 'decision', 'risk_score',
                                     'final_premium', 'exclusions', 'notes', 'processing_days'])
    return df


@kawa_tool(outputs={'underwriter_id': str, 'underwriter_name': str, 'experience_years': float, 'specialization': str,
                    'approval_rate': float, 'avg_processing_time': float, 'cases_handled': float})
def underwriter_performance_generator():
    fake = Faker()
    data = []
    specializations = ['Life Insurance', 'Health Insurance', 'Disability Insurance', 'Critical Illness', 'General']

    underwriter_ids = ['UW001', 'UW002', 'UW003', 'UW004', 'UW005']

    for underwriter_id in underwriter_ids:
        underwriter_name = fake.name()
        experience_years = np.random.uniform(2, 25)
        specialization = np.random.choice(specializations)
        approval_rate = np.random.uniform(0.60, 0.85)
        avg_processing_time = np.random.uniform(5, 20)
        cases_handled = np.random.uniform(800, 2000)

        data.append(
            [underwriter_id, underwriter_name, experience_years, specialization, approval_rate, avg_processing_time,
             cases_handled])

    df = pd.DataFrame(data, columns=['underwriter_id', 'underwriter_name', 'experience_years', 'specialization',
                                     'approval_rate', 'avg_processing_time', 'cases_handled'])
    return df


applications_dataset = app.create_dataset(
    name='Underwriting Applications',
    generator=underwriting_applications_generator,
)

decisions_dataset = app.create_dataset(
    name='Underwriting Decisions',
    generator=underwriting_decisions_generator,
)

underwriter_dataset = app.create_dataset(
    name='Underwriter Performance',
    generator=underwriter_performance_generator,
)

# -- DATA SECTION: end

# -- MODEL SECTION: start

model = app.create_model(
    dataset=applications_dataset,
)

decisions_rel = model.create_relationship(
    name='Decisions',
    dataset=decisions_dataset,
    link={'application_id': 'application_id'}
)

decisions_rel.add_column(
    name='decision',
    aggregation='FIRST',
    new_column_name='final_decision',
)

decisions_rel.add_column(
    name='risk_score',
    aggregation='FIRST',
    new_column_name='risk_assessment',
)

decisions_rel.add_column(
    name='final_premium',
    aggregation='FIRST',
    new_column_name='final_premium_amount',
)

decisions_rel.add_column(
    name='processing_days',
    aggregation='FIRST',
    new_column_name='processing_time',
)

underwriter_rel = model.create_relationship(
    name='Underwriters',
    dataset=underwriter_dataset,
    link={'underwriter_id': 'underwriter_id'}
)

underwriter_rel.add_column(
    name='underwriter_name',
    aggregation='FIRST',
    new_column_name='assigned_underwriter',
)

underwriter_rel.add_column(
    name='experience_years',
    aggregation='FIRST',
    new_column_name='underwriter_experience',
)

model.create_variable(
    name='Risk Threshold',
    kawa_type='decimal',
    initial_value=6.0,
)

model.create_variable(
    name='Target Processing Days',
    kawa_type='integer',
    initial_value=15,
)

model.create_metric(
    name='high_risk_applications',
    formula="""
    SUM(CASE WHEN "risk_assessment" > "Risk Threshold" THEN 1 ELSE 0 END)
    """,
)

model.create_metric(
    name='avg_processing_efficiency',
    formula="""
    AVG(CASE WHEN "processing_time" <= "Target Processing Days" THEN 1 ELSE 0 END) * 100
    """,
)

model.create_metric(
    name='premium_adjustment_rate',
    formula="""
    AVG(("final_premium_amount" - "premium_quoted") / "premium_quoted") * 100
    """,
)

model.create_metric(
    name='approval_rate_metric',
    formula="""
    SUM(CASE WHEN "final_decision" = 'Approved' THEN 1 ELSE 0 END) / COUNT("application_id") * 100
    """,
)

# -- MODEL SECTION: end

# -- DASHBOARD SECTION: start

main_page = app.create_page('Underwriting Dashboard')

explanation_col = main_page.create_section('Dashboard Overview', 1)
explanation_col.text_widget(
    content='This dashboard provides comprehensive insights into the health insurance underwriting process, tracking applications, decisions, and performance metrics.\n\nKey interactive elements include the Risk Threshold variable which determines high-risk application classification in the risk analysis widgets, and the Target Processing Days variable which affects processing efficiency calculations.\n\nModifying the Risk Threshold will impact the High Risk Applications count and risk distribution charts. Adjusting Target Processing Days will influence the Processing Efficiency metric and related performance indicators.\n\nUse this dashboard to monitor underwriting quality, identify bottlenecks, and optimize decision-making processes across the organization.'
)

kpi_col1, kpi_col2, kpi_col3 = main_page.create_section('Key Performance Indicators', 3)

kpi_col1.indicator_chart(
    title='High Risk Applications',
    indicator='high_risk_applications',
    source=model,
)

kpi_col2.indicator_chart(
    title='Processing Efficiency (%)',
    indicator='avg_processing_efficiency',
    source=model,
)

kpi_col3.indicator_chart(
    title='Overall Approval Rate (%)',
    indicator='approval_rate_metric',
    source=model,
)

chart_col1, chart_col2 = main_page.create_section('Application Analysis', 2)

chart_col1.bar_chart(
    title='Applications by Decision Status',
    x='final_decision',
    y='application_id',
    aggregation='COUNT',
    show_values=True,
    source=model,
)

chart_col2.pie_chart(
    title='Applications by Policy Type',
    labels='policy_type',
    values='application_id',
    aggregation='COUNT',
    show_values=True,
    show_labels=True,
    source=model,
)

trend_col1, trend_col2 = main_page.create_section('Trends and Distribution', 2)

trend_col1.line_chart(
    title='Monthly Application Volume',
    x='application_date',
    y='application_id',
    aggregation='COUNT',
    time_sampling='YEAR_AND_MONTH',
    area=True,
    source=model,
)

trend_col2.scatter_chart(
    title='Risk Score vs Premium Adjustment',
    granularity='application_id',
    x='risk_assessment',
    y='final_premium_amount',
    color='application_id',
    aggregation_color='COUNT',
    source=model,
)

performance_page = app.create_page('Underwriter Performance')

perf_explanation_col = performance_page.create_section('Performance Overview', 1)
perf_explanation_col.text_widget(
    content='This page focuses on individual underwriter performance metrics and workload distribution.\n\nTrack processing times, approval rates, and case volumes across different underwriters to identify training needs and optimize resource allocation.\n\nThe Target Processing Days variable affects the efficiency calculations shown in the processing time analysis charts.'
)

perf_col1, perf_col2 = performance_page.create_section('Performance Metrics', 2)

perf_col1.bar_chart(
    title='Average Processing Time by Underwriter',
    x='assigned_underwriter',
    y='processing_time',
    aggregation='AVERAGE',
    show_values=True,
    source=model,
)

perf_col2.bar_chart(
    title='Case Volume by Underwriter',
    x='assigned_underwriter',
    y='application_id',
    aggregation='COUNT',
    show_values=True,
    source=model,
)

perf_col3, perf_col4 = performance_page.create_section('Risk and Experience Analysis', 2)

perf_col3.scatter_chart(
    title='Experience vs Processing Time',
    granularity='underwriter_id',
    x='underwriter_experience',
    y='processing_time',
    aggregation_y='AVERAGE',
    color='application_id',
    aggregation_color='COUNT',
    source=model,
)

perf_col4.boxplot(
    title='Risk Score Distribution by Underwriter',
    x='assigned_underwriter',
    y='risk_assessment',
    source=model,
)

# -- DASHBOARD SECTION: end

app.publish()