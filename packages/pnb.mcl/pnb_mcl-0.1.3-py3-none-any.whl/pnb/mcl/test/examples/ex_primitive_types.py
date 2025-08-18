from datetime import datetime

def make_model_by_uri(meta_model):

    Model = meta_model.Model(
        name='Model',
        uri='http://Model',
        members=[
            meta_model.ConcreteClass(
                name='Class',
                members=[
                    meta_model.DataProperty('any_uri', meta_model.MCL.AnyURI),
                    meta_model.DataProperty('boolean', meta_model.MCL.Boolean),
                    meta_model.DataProperty('date_time', meta_model.MCL.DateTime),
                    meta_model.DataProperty('double', meta_model.MCL.Double),
                    meta_model.DataProperty('integer', meta_model.MCL.Integer),
                    meta_model.DataProperty('string', meta_model.MCL.String),
                    meta_model.DataProperty('unsigned_byte', meta_model.MCL.UnsignedByte)])])
    
    Model.add(Model.Class(
        name='InstanceA',
        any_uri='http://www.example.org',
        boolean=False,
        date_time=datetime.fromisoformat('2020-12-07T15:32:42'),
        double=-.3,
        integer=42,
        string='Hello world!',
        unsigned_byte=255
        ))
    
    Model.add(Model.Class(
        name='InstanceB',
        any_uri='http://www.example.org',
        boolean=True,
        date_time=datetime.fromisoformat('2020-12-07T15:32:42'),
        double=1e6,
        integer=-42,
        string='Hello world!',
        unsigned_byte=0
        ))

    return {model.uri: model for model in [Model]}
