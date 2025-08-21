from .app_variable import Variable
from .app_metric import Metric
from .app_relationship import Relationship


class DataModel:

    def __init__(self, kawa, name, application, dataset):
        self._dataset = dataset
        self._name = name
        self._k = kawa
        self._application = application

        self._sheet_id = None
        self._relationships = []
        self._metrics = []
        self._variables = []

    @property
    def sheet_id(self):
        return self._dataset.sheet_id

    @property
    def sheet(self):
        return self._dataset.sheet

    @property
    def application_id(self):
        return self._application.application_id

    def create_variable(self, name, kawa_type, initial_value):
        variable = Variable(
            kawa=self._k,
            sheet_id_supplier=lambda: self.sheet_id,
            name=name,
            kawa_type=kawa_type,
            initial_value=initial_value
        )
        self._variables.append(variable)

    def create_relationship(self, name, dataset, link):
        rel = Relationship(
            kawa=self._k,
            model=self,
            name=name,
            dataset=dataset,
            link=link,
        )
        self._relationships.append(rel)
        return rel

    def create_metric(self, name, formula=None, prompt=None):

        sql = None
        if formula:
            normalized = formula.strip().upper()
            if not normalized.startswith("SELECT"):
                sql = f"SELECT {formula}"
            else:
                sql = formula

        self._metrics.append(
            Metric(
                kawa=self._k,
                name=name,
                sql=sql,
                prompt=prompt,
            )
        )

    def sync(self):
        primary_datasource_id = self._dataset.datasource_id
        if primary_datasource_id is None:
            raise Exception('The underlying dataset has not been synced')

        control_panel = self._k.entities.control_panels().get_entity_by_id(self.sheet_id)

        for rel in self._relationships:
            rel.sync()

        for var in self._variables:
            var.sync(control_panel=control_panel)

        for metric in self._metrics:
            metric.sync(sheet=self.sheet)
