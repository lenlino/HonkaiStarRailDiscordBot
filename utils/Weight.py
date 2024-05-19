from pydantic import BaseModel


class Weight1(BaseModel):
    HPDelta: float = 0.0


class Weight2(BaseModel):
    AttackDelta: float = 0.0


class Weight3(BaseModel):
    HPAddedRatio: float = 0.0
    AttackAddedRatio: float = 0.0
    DefenceAddedRatio: float = 0.0
    CriticalChanceBase: float = 0.0
    CriticalDamageBase: float = 0.0
    HealRatioBase: float = 0.0
    StatusProbabilityBase: float = 0.0


class Weight4(BaseModel):
    HPAddedRatio: float = 0.0
    AttackAddedRatio: float = 0.0
    DefenceAddedRatio: float = 0.0
    SpeedDelta: float = 0.0


class Weight5(BaseModel):
    HPAddedRatio: float = 0.0
    AttackAddedRatio: float = 0.0
    DefenceAddedRatio: float = 0.0
    PhysicalAddedRatio: float = 0.0
    FireAddedRatio: float = 0.0
    IceAddedRatio: float = 0.0
    ThunderAddedRatio: float = 0.0
    WindAddedRatio: float = 0.0
    QuantumAddedRatio: float = 0.0
    ImaginaryAddedRatio: float = 0.0


class Weight6(BaseModel):
    BreakDamageAddedRatioBase: float = 0.0
    SPRatioBase: float = 0.0
    HPAddedRatio: float = 0.0
    AttackAddedRatio: float = 0.0
    DefenceAddedRatio: float = 0.0


class WeightSub(BaseModel):
    HPDelta: float = 0.0
    AttackDelta: float = 0.0
    DefenceDelta: float = 0.0
    HPAddedRatio: float = 0.0
    AttackAddedRatio: float = 0.0
    DefenceAddedRatio: float = 0.0
    SpeedDelta: float = 0.0
    CriticalChanceBase: float = 0.0
    CriticalDamageBase: float = 0.0
    StatusProbabilityBase: float = 0.0
    StatusResistanceBase: float = 0.0
    BreakDamageAddedRatioBase: float = 0.0


class WeightMain(BaseModel):
    w1: Weight1 = Weight1()
    w2: Weight2 = Weight2()
    w3: Weight3 = Weight3()
    w4: Weight4 = Weight4()
    w5: Weight5 = Weight5()
    w6: Weight6 = Weight6()


class Lang(BaseModel):
    jp: str = ""
    en: str = ""


class Weight(BaseModel):
    main: WeightMain = WeightMain()
    weight: WeightSub = WeightSub()
    max: float = 0.0
    lang: Lang = Lang()
