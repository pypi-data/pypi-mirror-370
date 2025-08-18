def make_model_by_uri(meta_model):

    ModelCore = meta_model.Model(
        name='ModelCore',
        uri='http://ModelCore',
        members=[meta_model.AbstractClass(name='ConceptualModel')])

    ModelProcess = meta_model.Model(
        name='ModelProcess',
        uri='http://ModelProcess')
    ModelProcess.add(meta_model.Package(
        name='Base',
        members=[
            meta_model.ConcreteClass(
                name='ProcessStep',
                superTypes=[ModelCore.ConceptualModel],
                members=[
                    meta_model.DataProperty(
                        name='StepNumber',
                        lower=0,
                        upper=1,
                        type_=meta_model.MCL.String,
                        isOrdered=False,
                        isUnique=False)])]))
    ModelProcess.Base.ProcessStep.add(
        meta_model.ReferenceProperty(
            name='RelatedSteps',
            lower=0,
            upper=None,
            type_=ModelProcess.Base.ProcessStep,
            isOrdered=False,
            isUnique=True,
            oppositeLower=0,
            oppositeUpper=None))
    ModelProcess.Base.ProcessStep.add(
        meta_model.CompositionProperty(
            name='SubSteps',
            lower=0,
            upper=None,
            type_=ModelProcess.Base.ProcessStep,
            isOrdered=False))
    ModelProcess.add(meta_model.Package(
        name='Steps',
        members=[
            meta_model.ConcreteClass(
                name='Pumping',
                superTypes=[ModelProcess.Base.ProcessStep])]))

    ModelProcess.Steps.Pumping(
                StepNumber='step1')

    ModelInstance1 = meta_model.Model(
        name='ModelInstance1',
        uri='http://ModelInstance1',
        members=[
            step1:=ModelProcess.Steps.Pumping(
                StepNumber='step1')])

    ModelInstance2a = meta_model.Model(
        name='ModelInstance2',
        uri='http://ModelInstance2a',
        members=[
            step2a1:=ModelProcess.Steps.Pumping(
                name='Step1',
                StepNumber='step2a1'),
            step2a2:=ModelProcess.Steps.Pumping(
                StepNumber='step2a2')])

    ModelInstance2b = meta_model.Model(
        name='ModelInstance2',
        uri='http://ModelInstance2b',
        members=[
            step2b:=ModelProcess.Steps.Pumping(
                name='Step',
                StepNumber='step2b')])

    ModelInstance3 = meta_model.Model(
        name='ModelInstance3',
        uri='http://ModelInstance3',
        members=[
            ModelProcess.Steps.Pumping(
                StepNumber='step31',
                SubSteps=[
                    step32:=ModelProcess.Steps.Pumping(
                        name='Step',
                        StepNumber='step32'),
                    #step2a2 # TODO
                    ])])

    step1.RelatedSteps = [step2a1, step2b]
    step2a1.RelatedSteps = [step2a2, step32]
    step2b.RelatedSteps = [step2a1]

    return {model.uri: model for model in [
        ModelCore, ModelProcess, ModelInstance1, ModelInstance2a, ModelInstance2b, ModelInstance3]}
