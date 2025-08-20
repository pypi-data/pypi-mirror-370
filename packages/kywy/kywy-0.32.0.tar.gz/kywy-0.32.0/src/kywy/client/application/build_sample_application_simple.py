import pandas as pd
from datetime import date, datetime
from .application_builder import ApplicationBuilder
from .app_dataset import DataSet
from ...client.kawa_client import KawaClient
from ...client.kawa_decorators import kawa_tool


def kawa():
    k = KawaClient(kawa_api_url='http://localhost:4200')
    k.set_api_key(api_key_file='/Users/emmanuel/doc/local-pristine/.key')
    k.set_active_workspace_id(workspace_id='79')
    return k


app = kawa().app(
    application_name='Charlotte9',
    sidebar_color='#2c3e50',
)


@kawa_tool(outputs={'product_name': str, 'sales': float, 'ok': str})
def simple_data_generator():
    fake = Faker()
    data = []
    for i in range(50):
        product_name = fake.word().capitalize()
        sales = np.random.uniform(100, 1000)
        ok = 'ok!::'
        data.append([product_name, sales, ok])
    df = pd.DataFrame(data, columns=['product_name', 'sales', 'ok'])
    return df


simple_dataset = app.create_dataset('Simple Data', generator=simple_data_generator)
other_dataset = app.create_dataset('Other Data ?', generator=simple_data_generator)

model = app.create_model(simple_dataset)

model.create_variable('Threshold', kawa_type='decimal', initial_value=0.0)
model.create_metric('Sum Of Sales', formula='"product_name"')
model.create_metric('Avg Of Sales', formula='AVG("sales")')
model.create_metric('Twice The Sales .', formula='3 * "sales"')
model.create_metric('Sales Above Threshold', formula='"sales" > "Threshold"')

relationship = model.create_relationship(
    name='Some stupid link',
    dataset=other_dataset,
    link={'product_name': 'product_name'},
)

relationship.add_column(
    name='sales',
    aggregation='SUM',
    new_column_name='S'
)

orders_page = app.create_page('Orders Analytics')
col1 = orders_page.create_section('Profit', 1)
col1.bar_chart(
    title='Chart I',
    x='product_name',
    y='sales',
)

col1, col2 = orders_page.create_section('Profit II', 2)
col1.boxplot(
    title='Chart II',
    x='product_name',
    y='sales',
)
col2.bar_chart(
    title='Chart III',
    x='product_name',
    y='sales',
)

app.create_text_filter(
    name='Product Name II',
    filtered_column='product_name',
)

app.create_ai_agent(
    name='BinaryBard',
    instructions='''
    You are an expert in data analytics. 
    Always answer with as much precision as possible.
    ''',
    color="#040506",
)

app.publish()
