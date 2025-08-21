import copy
import datetime
import platform
import subprocess  # noqa: S404
import sys
from pathlib import Path
from textwrap import dedent
from typing import ClassVar, Literal
from typing import Union as _Union

from pydantic import (
    BaseModel,
    Field,
    NonNegativeInt,
    PositiveInt,
    field_validator,
    model_validator,
)

if sys.version_info >= (3, 11):
    from typing import assert_never
else:

    def assert_never(value):
        msg = f"Expected code to be unreachable, but got: {value}"
        raise AssertionError(msg)


_TRANS = str.maketrans(r":-+*/'(){}^=<>$ |#?,\¥", "_" * 22)  # 文字列変換用

NonNegativeIntOrInf = _Union[NonNegativeInt, Literal["inf"]]  # mypyで型と認識させるため_Union使用 # noqa: UP007
NonNegativeDict = dict[tuple[NonNegativeInt, NonNegativeIntOrInf], NonNegativeInt]
PositiveDict = dict[tuple[NonNegativeInt, NonNegativeIntOrInf], PositiveInt]
DirectionType = Literal["<=", ">=", "="]
ResourceType = Literal["", "break", "max"]


def to_tuple(key: str | tuple, type_: type):
    return map(type_, key.split(",")) if isinstance(key, str) else key


def key_to_tuple(_cls, member: dict, type_: type) -> dict:
    return {to_tuple(key, type_): value for key, value in member.items()}


def deserialize(member: str):
    def _decorator(func):
        f = field_validator(member, mode="before")
        return f(classmethod(func))

    return _decorator


class Parameters(BaseModel):
    """OptSeq parameter class to control the operation of OptSeq.

    - param  TimeLimit: Limits the total time expended (in seconds). Positive integer. Default=600.
    - param  OutputFlag: Controls the output log. Boolean. Default=False (0).
    - param  RandomSeed: Sets the random seed number. Integer. Default=1.
    - param  ReportInterval: Controls the frequency at which log lines are printed (iteration number).
             Default=1073741823.
    - param  Backtruck: Controls the maximum backtrucks. Default=1000.
    - param  MaxIteration: Sets the maximum numbers of iterations. Default=1073741823.
    - param  Initial: =True if the user wants to set an initial activity list. Default = False.
            Note that the file name of the activity list must be "optseq_best_act_data.txt."
    - param  Tenure: Controls a parameter of tabu search (initial tabu tenure). Default=1.
    - param  Neighborhood: Controls a parameter of tabu search (neighborhood size). Default=20.
    - param  Makespan: Sets the objective function.
            Makespan is True if the objective is to minimize the makespan (maximum completion time),
            is False otherwise, i.e., to minimize the total weighted tardiness of activities.
            Default=False.
    """

    TimeLimit: PositiveInt = 600
    OutputFlag: bool = False  # off
    RandomSeed: int = 1
    ReportInterval: PositiveInt = 1073741823
    Backtruck: PositiveInt = 1000  # TODO: Backtrackに変更
    MaxIteration: PositiveInt = 1073741823
    Initial: bool = False
    Tenure: PositiveInt = 1
    Neighborhood: PositiveInt = 20
    Makespan: bool = False

    def __str__(self) -> str:
        return dedent(
            f"""\
            TimeLimit = {self.TimeLimit}
            OutputFlag = {self.OutputFlag}
            RandomSeed = {self.RandomSeed}
            ReportInterval = {self.ReportInterval}
            Backtruck = {self.Backtruck}
            Initial = {self.Initial}
            Tenure = {self.Tenure}
            Neighborhood = {self.Neighborhood}
            makespan = {self.Makespan}""",
        )


class State(BaseModel):
    """OptSeq state class.

    You can create a state object by adding a state to a model (using Model.addState)
    instead of by using a State constructor.
    - Arguments:
        - name: Name of state. Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.
    """

    ID: ClassVar[int] = 0
    name: str = ""
    Value: dict[NonNegativeInt, NonNegativeInt] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _post_init(self):
        if not self.name:
            self.name = f"__s{State.ID}"
            State.ID += 1
        if not isinstance(self.name, str):
            msg = "State name must be a string"
            raise TypeError(msg)

        # convert illegal characters into _ (underscore)
        self.name = self.name.translate(_TRANS)
        self.model_fields_set.add("name")
        return self

    def __str__(self) -> str:
        ret = [f"state {self.name} "]
        for k, v in self.Value.items():
            ret.append(f"time {k} value {v} ")
        return " ".join(ret)

    def addValue(self, time: NonNegativeInt = 0, value: NonNegativeInt = 0) -> None:
        """Adds a value to the state

        - Arguments:
            - time: the time at which the state changes.
            - value: the value that the state changes to
        - Example usage:
        >>> state.addValue(time=5, value=1)
        """
        if isinstance(time, int) and isinstance(value, int):
            self.Value[time] = value
            self.model_fields_set.add("Value")
        else:
            print(f"time and value of the state {self.name} must be integer")
            raise TypeError


class Mode(BaseModel):
    """OptSeq mode class.

    - Arguments:
        - name: Name of mode (sub-activity).
                Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.
                Also you cannot use "dummy" for the name of a mode.
                - duration(optional): Processing time of mode. Default=0.

    - Attributes:
        - requirement:
            dictionary that maps a pair of resource name and resource type (rtype) to requirement dictionary.
            Requirement dictionary maps intervals (pairs of start time and finish time) to amounts of requirement.
            Resource type (rtype) is ""(standard resource type), "break" or "max."
        - breakable: dictionary that maps breakable intervals to maximum break times.
        - parallel:  dictionary that maps parallelizable intervals to maximum parallel numbers.
        - state: dictionary that maps states to the tuples of values.
    """

    ID: ClassVar[int] = 0
    name: str = ""
    duration: NonNegativeInt = 1
    requirement: dict[tuple[str, str], NonNegativeDict] = Field(default_factory=dict)
    breakable: PositiveDict = Field(default_factory=dict)
    parallel: dict[tuple[PositiveInt, PositiveInt], PositiveInt] = Field(default_factory=dict)
    state: dict[str, list[tuple[int, int]]] = Field(default_factory=dict)

    def __init__(self, name: str | None = None, duration: NonNegativeInt | None = None, **data):
        if name is not None:
            data["name"] = name
        if duration is not None:
            data["duration"] = duration
        super().__init__(**data)

    @model_validator(mode="after")
    def _post_init(self):
        if not self.name:
            self.name = f"__m{Mode.ID}"
            Mode.ID += 1
        if self.name == "dummy":
            msg = "'dummy' cannot be used as a mode name"
            print(msg)
            raise NameError(msg)
        if not isinstance(self.name, str):
            msg = "Mode name must be a string"
            raise TypeError(msg)

        self.name = self.name.translate(_TRANS)
        self.model_fields_set.add("name")
        return self

    def __str__(self) -> str:  # noqa: C901 PLR0912
        ret = [f" duration {self.duration} "]

        for (r, rtype), dct in self.requirement.items():
            for interval, cap in dct.items():
                s, t = interval
                if rtype == "max":
                    ret.append(f" {r} max interval {s} {t} requirement {cap} ")
                elif rtype == "break":
                    ret.append(f" {r} interval break {s} {t} requirement {cap} ")
                elif not rtype:
                    ret.append(f" {r} interval {s} {t} requirement {cap} ")
                else:
                    assert_never(rtype)  # type: ignore[arg-type]

        # break
        for interval, cap in self.breakable.items():
            s, t = interval
            if cap == "inf":
                ret.append(f" break interval {s} {t} ")
            else:
                ret.append(f" break interval {s} {t} max {cap} ")

        # parallel
        for interval, cap in self.parallel.items():
            s, t = interval
            if cap == "inf":
                ret.append(f" parallel interval {s} {t} ")
            else:
                ret.append(f" parallel interval {s} {t} max {cap} ")

        # state
        for s, lst in self.state.items():
            for f, t in lst:
                ret.append(f" {s} from {f} to {t} ")

        return " \n".join(ret)

    def addState(self, state: State, fromValue: int = 0, toValue: int = 0) -> None:
        """Adds a state change information to the mode.

        - Arguments:
            - state: State object to be added to the mode.
            - fromValue: the value from which the state changes by the mode
            - toValue:  the value to which the state changes by the mode

        - Example usage:

        >>> mode.addState(state1, 0, 1)

        defines that state1 is changed from 0 to 1.
        """
        if not isinstance(fromValue, int) or not isinstance(toValue, int):
            msg = f"time and value of the state {self.name} must be integer"
            print(msg)
            raise TypeError(msg)
        if state.name not in self.state:
            self.state[state.name] = []
        self.state[state.name].append((fromValue, toValue))
        self.model_fields_set.add("state")

    def addResource(
        self,
        resource: "Resource",
        requirement: (int | dict[tuple[NonNegativeInt, NonNegativeIntOrInf], NonNegativeInt] | None) = None,
        rtype: ResourceType = "",
    ):
        """Adds a resource to the mode.

        - Arguments:
            - resource: Resource object to be added to the mode.
            - requirement:
                dictionary that maps intervals (pairs of start time and finish time) to amounts of requirement.
                It may be an integer; in this case, it is converted into the dictionary {(0, "inf"): requirement}.
            - rtype (optional): Type of resource to be added to the mode.
                ""(standard resource type; default), "break" or "max."

        - Example usage:

        >>> mode.addResource(worker, {(0, 10): 1})

        defines worker resource that uses 1 unit for 10 periods.

        >>> mode.addResource(machine, {(0, "inf"): 1}, "break")

        defines machine resource that uses 1 unit during break periods.

        >>> mode.addResource(machine, {(0, "inf"): 1}, "max")

        defines machine resource that uses 1 unit during parallel execution.
        """
        if isinstance(requirement, int):  # 引数を辞書に変換
            requirement = {(0, "inf"): requirement}

        if not isinstance(resource.name, str) or not isinstance(requirement, dict):
            print(
                f"type error in adding a resource {resource.name} to activity's mode "
                f"{self.name}: requirement type is {type(requirement)}",
            )
            msg = f"type error in adding a resource {resource.name} to activity {self.name}"
            raise TypeError(msg)
        if rtype in {"", "break", "max"}:
            if (resource.name, rtype) not in self.requirement:
                # generate an empty dic.
                self.requirement[resource.name, rtype] = {}
            # TODO 確認
            data = copy.deepcopy(self.requirement[resource.name, rtype])
            data.update(requirement)
            self.requirement[resource.name, rtype] = data
            self.model_fields_set.add("requirement")
        else:
            assert_never(rtype)  # type: ignore[arg-type]

    def addBreak(
        self,
        start: NonNegativeInt = 0,
        finish: NonNegativeInt = 0,
        maxtime: NonNegativeIntOrInf = "inf",
    ) -> None:
        """Sets breakable information to the mode.

        - Arguments:
            - start(optional): Earliest break time. Non-negative integer. Default=0.
            - finish(optional): Latest break time.  Non-negative integer or "inf." Default=0.
                Interval (start, finish) defines a possible break interval.
            - maxtime(optional): Maximum break time. Non-negative integer or "inf." Default="inf."

        - Example usage:

        >>> mode.addBreak(0, 10, 1)

        defines a break between (0, 10) for one period.
        """
        # TODO 確認
        # data = copy.deepcopy(self.breakable)
        # data.update({(start, finish): maxtime})
        self.breakable[start, finish] = maxtime
        self.model_fields_set.add("breakable")

    def addParallel(
        self,
        start: PositiveInt = 1,
        finish: PositiveInt = 1,
        maxparallel: NonNegativeIntOrInf = "inf",
    ):
        """Sets parallel information to the mode.

        - Arguments:
            - start(optional): Smallest job index executable in parallel. Positive integer. Default=1.
            - finish(optional): Largest job index executable in parallel. Positive integer or "inf." Default=1.
            - maxparallel(optional): Maximum job numbers executable in parallel.
                Non-negative integer or "inf." Default="inf."

        - Example usage:

        >>> mode.addParallel(1, 1, 2)
        """
        # data = copy.deepcopy(self.parallel)
        # data.update({(start, finish): maxparallel})
        self.parallel[start, finish] = maxparallel
        self.model_fields_set.add("parallel")


class Activity(BaseModel):
    """OptSeq activity class.

    You can create an activity object by adding an activity to a model (using Model.addActivity)
    instead of by using an Activity constructor.

    - Arguments:
            - name: Name of activity. Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.
                    Also you cannot use "source" and "sink" for the name of an activity.
            - duedate(optional): Due date of activity. A non-negative integer or string "inf."
            - backward(optional): True if activity is distached backwardly, False (default) otherwise.
            - weight(optional): Penalty of one unit of tardiness. Positive integer.
            - autoselect(optional):
                True or False flag that indicates the activity selects the mode automatically or not.
    """

    ID: ClassVar[int] = 0
    name: str = ""
    duedate: NonNegativeIntOrInf = "inf"
    backward: bool = False  # 後ろ詰め
    weight: PositiveInt = 1
    autoselect: bool = False
    quadratic: bool = False
    modes: list[Mode] = Field(default_factory=list)  # list of mode objects
    start: NonNegativeInt = 0
    completion: NonNegativeInt = 0
    execute: NonNegativeDict = Field(default_factory=dict)
    selected: Mode | None = None

    # JSONで文字列になった辞書のキーを戻す処理(classmethodであることに注意)
    @deserialize("execute")
    def deserialize_execute(cls, member: dict) -> dict:  # noqa: N805
        return key_to_tuple(cls, member, int)

    @model_validator(mode="after")
    def _post_init(self):
        if self.name in {"source", "sink"}:
            print(" 'source' and 'sink' cannot be used as an activity name")
            raise NameError

        if not isinstance(self.name, str):
            msg = "Activity name must be a string"
            raise TypeError(msg)

        if not self.name:
            self.name = f"__a{Activity.ID}"
            Activity.ID += 1

        # convert illegal characters into _ (underscore)
        self.name = self.name.translate(_TRANS)
        return self

    def __str__(self) -> str:
        ret = [f"activity {self.name}"]
        if self.duedate != "inf":
            if self.backward:
                ret.append(f" backward duedate {self.duedate} ")
            else:
                ret.append(f" duedate {self.duedate} ")
            ret.append(f" weight {self.weight} ")
            if self.quadratic:
                ret.append(" quad ")

        # １つのモードと２つ以上を区別しない実装
        if self.autoselect:
            ret.append(" autoselect ")
        # multiple modes
        ret.extend([f" {m.name} " for m in self.modes])

        # TODO 確認 スペース必要？
        return " \n".join(ret)

    def addModes(self, *modes: Mode) -> None:
        """Adds a mode or modes to the activity.

        - Arguments:
            - modes: One or more mode objects.

        - Example usage:

        >>> activity.addModes(mode1, mode2)
        """
        for mode in modes:
            self.modes.append(mode)
        self.model_fields_set.add("modes")


ActivityOrLiteral = Activity | Literal["source", "sink"]
_default_activity = Activity().model_dump()


class Resource(BaseModel):
    """OptSeq resource class.

    - Arguments:
        - name: Name of resource.
                Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.
        - capacity (optional):
        Capacity dictionary of the renewable (standard) resource.
        Capacity dictionary maps intervals (pairs of start time and finish time) to amounts of capacity.
        If it is given by a positive integer, it is converted into the dictionary {(0, "inf"): capacity}.
        - rhs (optional): Right-hand-side constant of nonrenewable resource constraint.
        - direction (optional): Direction (or sense) of nonrenewable resource constraint; "<=" (default) or ">=".
        - weight (optional): Weight of nonrenewable resource to compute the penalty for violating the constraint.
                             Non-negative integer or "inf" (default).

    - Attributes:
        - capacity: Capacity dictionary of the renewable (standard) resource.
        - rhs: Right-hand-side constant of nonrenewable resource constraint.
        - direction: Direction (or sense) of nonrenewable resource constraint; "<=" (default) or "=" or ">=".
        - terms: List of terms in left-hand-side of nonrenewable resource.
                Each term is a tuple of coefficient, activity and mode.
        - weight: Weight of nonrenewable resource to compute the penalty for violating the constraint.
                Non-negative integer or "inf" (default).
        - residual: Residual dictionary of the renewable (standard) resource.
    """

    ID: ClassVar[int] = 0
    name: str = ""
    # TODO 確認 intは初期化時のみとマニュアルに
    capacity: NonNegativeDict | int = Field(default_factory=dict)
    rhs: int = 0
    # TODO 確認 =の代わりに==は？
    direction: DirectionType = "<="
    weight: NonNegativeIntOrInf = "inf"
    terms: list[tuple[int, Activity, Mode]] = Field(default_factory=list)
    residual: NonNegativeDict = Field(default_factory=dict)

    @model_validator(mode="after")
    def _post_init(self):
        if not self.name:
            self.name = f"__r{Resource.ID}"
            Resource.ID += 1
        if not isinstance(self.name, str):
            msg = "Resource name must be a string"
            raise TypeError(msg)

        # convert illegal characters into _ (underscore)
        self.name = self.name.translate(_TRANS)
        self.model_fields_set.add("name")
        if isinstance(self.capacity, int):
            self.capacity = {(0, "inf"): self.capacity}
        self.model_fields_set.add("capacity")
        return self

    def __str__(self) -> str:
        ret = []
        assert isinstance(self.capacity, dict)
        ret.append(f"resource {self.name} ")
        capList = []
        for interval, cap in self.capacity.items():
            (s, t) = interval
            capList.append((s, t, cap))
        # capList.sort()
        for s, t, cap in capList:
            ret.append(f" interval {s} {t} capacity {cap} ")
        # ret.append("\n")
        return " \n".join(ret)

    def addCapacity(self, start: NonNegativeInt = 0, finish: NonNegativeInt = 0, amount: NonNegativeInt = 1) -> None:
        """Adds a capacity to the resource.

        - Arguments:
            - start(optional): Start time. Non-negative integer. Default=0.
            - finish(optional): Finish time. Non-negative integer. Default=0.
                Interval (start, finish) defines the interval during which the capacity is added.
            - amount(optional): The amount to be added to the capacity. Positive integer. Default=1.

        - Example usage:

        >>> manpower.addCapacity(0, 5, 2)
        """
        assert isinstance(self.capacity, dict)  # for mypy
        # data = copy.deepcopy(self.capacity)
        # data.update({(start, finish): amount})
        self.capacity[start, finish] = amount
        self.model_fields_set.add("capacity")

    def printConstraint(self) -> str:
        """Returns the information of the linear constraint.

        The constraint is expanded and is shown in a readable format.
        """
        f = [f"nonrenewable weight {self.weight} "]
        if self.direction == ">=":
            for coeff, var, value in self.terms:
                f.append(f"{-coeff}({var.name},{value.name}) ")
            f.append(f"<={-self.rhs} \n")
        elif self.direction == "=":
            for coeff, var, value in self.terms:
                f.append(f"{coeff}({var.name},{value.name}) ")
            f.extend([f"<={self.rhs} \n", f"nonrenewable weight {self.weight} "])
            for coeff, var, value in self.terms:
                f.append(f"{-coeff}({var.name},{value.name}) ")
            f.append(f"<={-self.rhs} \n")
        else:
            assert self.direction == "<="
            for coeff, var, value in self.terms:
                f.append(f"{coeff}({var.name},{value.name}) ")
            f.append(f"<={self.rhs} \n")

        return "".join(f)

    def addTerms(
        self,
        coeffs: int | list[int],
        vars: Activity | list[Activity],  # noqa: A002
        values: Mode | list[Mode],
    ) -> None:
        """Add new terms into left-hand-side of nonrenewable resource constraint.

        - Arguments:
            - coeffs: Coefficients for new terms; either a list of coefficients or a single coefficient.
            The three arguments must have the same size.
            - vars: Activity objects for new terms; either a list of activity objects or a single activity object.
            The three arguments must have the same size.
            - values: Mode objects for new terms; either a list of mode objects or a single mode object.
            The three arguments must have the same size.

        - Example usage:

        >>> budget.addTerms(1, act, express)

        adds one unit of nonrenewable resource (budget) if activity "act" is executed in mode "express."
        """
        if not isinstance(coeffs, list):
            if isinstance(vars, list) or isinstance(values, list):
                msg = "vars must be Activity, values must be Mode"
                raise TypeError(msg)
            self.terms.append((coeffs, vars, values))
        else:
            if not isinstance(vars, list) or not isinstance(values, list):
                msg = "vars, values must be lists"
                raise TypeError(msg)
            for args in zip(coeffs, vars, values, strict=False):
                self.terms.append(args)
        self.model_fields_set.add("terms")

    def setRhs(self, rhs: int = 0) -> None:
        """Sets the right-hand-side of linear constraint.

        - Argument:
            - rhs: Right-hand-side of linear constraint.

        - Example usage:

        >>> L.setRhs(10)
        """
        self.rhs = rhs
        self.model_fields_set.add("rhs")

    def setDirection(self, direction: DirectionType = "<=") -> None:
        if direction in {"<=", ">=", "="}:
            self.direction = direction
            self.model_fields_set.add("direction")
        else:
            msg = "direction setting error; direction should be one of '<=' or '>=' or '='"
            print(msg)
            raise NameError(msg)


class Temporal(BaseModel):
    """OptSeq temporal class.

    A temporal constraint has the following form:

        predecessor's completion (start) time + delay <=
                        successor's start (completion) time.

    Parameter "delay" can be negative.

    - Arguments:
        - pred: Predecessor (an activity object) or string "source."
                Here, "source" specifies a dummy activity that precedes all other activities and starts at time 0.
        - succ: Successor (an activity object) or string "source."
                Here, "source" specifies a dummy activity that precedes all other activities and starts at time 0.
        - tempType (optional): String that differentiates the temporal type.
            "CS" (default)=Completion-Start, "SS"=Start-Start,
            "SC"= Start-Completion, "CC"=Completion-Completion.
        - delay (optional): Time lag between the completion (start) times of two activities.
        - pred_mode (optional): Predecessor's mode
        - succ_mode (optional): Successor's mode

    - Attributes:
        - pred: Predecessor (an activity object) or string "source."
        - succ: Successor (an activity object) or string "source."
        - type: String that differentiates the temporal type.
            "CS" (default)=Completion-Start, "SS"=Start-Start,
            "SC"= Start-Completion, "CC"=Completion-Completion.
        - delay: Time lag between the completion (start) times of two activities. default=0.
    """

    pred: ActivityOrLiteral  # activity or "source" or "sink"
    succ: ActivityOrLiteral
    type: Literal["CS", "SS", "SC", "CC"] = "CS"
    delay: int = 0
    pred_mode: Mode | None = None
    succ_mode: Mode | None = None

    @model_validator(mode="after")
    def _post_init(self):
        if self.pred_mode is not None:
            assert isinstance(self.pred, Activity)
            if self.pred_mode not in self.pred.modes:
                msg = f"Mode {self.pred_mode.name} is not in activity {self.pred.name}"
                raise ValueError(msg)
        if self.succ_mode is not None:
            assert isinstance(self.succ, Activity)
            if self.succ_mode not in self.succ.modes:
                msg = f"Mode {self.succ_mode.name} is not in activity {self.succ.name}"
                raise ValueError(msg)
        return self

    def __str__(self) -> str:
        pred = self.pred if isinstance(self.pred, str) else self.pred.name
        succ = self.succ if isinstance(self.succ, str) else self.succ.name
        if self.pred_mode is None and self.succ_mode is None:
            # モードに依存しない時間制約
            ret = [f"temporal {pred} {succ}"]
            ret.append(f" type {self.type} delay {self.delay} ")
        else:
            # source, sink以外の場合で， 片方だけモード指定して，複数モードがある場合にはエラー
            if self.pred != "source" and self.succ != "sink":
                assert isinstance(self.pred, Activity)
                assert isinstance(self.succ, Activity)
                if self.pred_mode is None and self.succ_mode is not None:
                    msg = f"The mode of activity {self.pred.name} is not specified!"
                    raise ValueError(msg)
                if self.pred_mode is not None and self.succ_mode is None:
                    msg = f"The mode of activity {self.succ.name} is not specified!"
                    raise ValueError(msg)

            pred_mode = self.pred_mode.name if isinstance(self.pred_mode, Mode) else "dummy"
            succ_mode = self.succ_mode.name if isinstance(self.succ_mode, Mode) else "dummy"
            ret = [f"temporal {pred} mode {pred_mode} {succ} mode {succ_mode}"]
            ret.append(f" type {self.type} delay {self.delay} ")

        # print(self.pred_mode, self.succ_mode, ret)
        return " ".join(ret)


class Model(BaseModel):
    """OptSeq model class.
    - Attributes:
        - activities: dictionary that maps activity names to activity objects in the model.
        - modes: dictionary that maps mode names to mode objects in the model.
        - resources:  dictionary that maps resource names to resource objects in the model.
        - temporals: dictionary that maps pairs of activity names to temporal constraint objects in the model.
        - Params: Object including all the parameters of the model.

        - act: List of all the activity objects in the model.
        - res: List of all the resource objects in the model.
        - tempo: List of all the temporal constraint objects in the model.
    """

    name: str = ""
    # set of activities maintained by a dictionary
    activities: dict[str, Activity] = Field(default_factory=dict)
    # set of modes maintained by a dictionary
    modes: dict[str, Mode] = Field(default_factory=dict)
    # set of resources maintained by a dictionary
    resources: dict[str, Resource] = Field(default_factory=dict)
    # set of temporal constraints maintained by a dictionary
    temporals: dict[str, Temporal] = Field(default_factory=dict)
    # set of states maintained by a dictionary
    states: dict[str, State] = Field(default_factory=dict)

    act: list[Activity] = Field(default_factory=list)  # list of activity objects
    res: list[Resource] = Field(default_factory=list)  # list of resource objects
    tempo: list[Temporal] = Field(default_factory=list)  # list of temporal constraint's objects
    state: list[State] = Field(default_factory=list)  # list of state objects

    Params: Parameters = Field(default_factory=Parameters)  # control parameters' class
    Status: int = 10  # unsolved
    ObjVal: NonNegativeInt | None = None  # best solution value

    def __str__(self):  # noqa: C901
        ret = [f"Model:{self.name}"]
        ret.extend([f"number of activities= {len(self.act)}", f"number of resources= {len(self.res)}"])

        if len(self.res):
            ret.append("\nResource Information")
            for res in self.res:
                ret.append(str(res))
                if len(res.terms) > 0:
                    ret.append(res.printConstraint())

        for a in self.act:
            # if len(a.modes) >= 2:
            for m in a.modes:
                self.modes[m.name] = m

        if len(self.modes):
            ret.append("\nMode Information")
            for i in self.modes:
                # ret.append("{0}\n{1}".format(i, self.modes[i]))
                ret.extend([str(i), str(self.modes[i])])

        if len(self.act):
            ret.append("\nActivity Information")
            ret.extend([str(act) for act in self.act])

        if len(self.tempo):
            ret.append("\nTemporal Constraint Information")
            ret.extend([str(t) for t in self.tempo])

        if len(self.state):
            ret.append("\nState Information")
            ret.extend([str(s) for s in self.state])

        return "\n".join(ret)

    def addActivity(  # noqa: PLR0913
        self,
        name="",
        duedate="inf",
        weight=1,
        *,
        backward=False,
        autoselect=False,
        quadratic=False,
    ):
        """Add an activity to the model.

        - Arguments:
            - name: Name for new activity. A string object except "source" and "sink".
                    Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.
            - duedate(optional): Duedate of activity. A non-negative integer or string "inf."
            - backward(optional): True if activity is distached backwardly, False (default) otherwise.
            - weight(optional): Penalty of one unit of tardiness. Positive integer.
            - autoselect(optional):
                True or False flag that indicates the activity selects the mode automatically or not.

        - Return value: New activity object.

        - Example usage:

        >>> a = model.addActivity("act1")

        >>> a = model.addActivity(name="act1", duedate=20, weight=100)

        >>> a = model.addActivity("act1", 20, 100)
        """
        dc = {
            "name": name,
            "duedate": duedate,
            "backward": backward,
            "weight": weight,
            "autoselect": autoselect,
            "quadratic": quadratic,
        }
        dc = {k: v for k, v in dc.items() if v != _default_activity[k]}
        activity = Activity.model_validate(dc)
        self.act.append(activity)
        self.model_fields_set.add("act")
        # self.activities[activity.name]=activity
        return activity

    def addResource(self, name="", capacity=None, rhs=0, direction="<=", weight="inf"):
        """Add a resource to the model.

        - Arguments:
            - name: Name for new resource. Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.
            - capacity (optional): Capacity dictionary of the renewable (standard) resource.
            - Capacity dictionary maps intervals (pairs of start time and finish time) to amounts of capacity.
            - rhs (optional): Right-hand-side constant of nonrenewable resource constraint.
            - direction (optional):
                Direction (or sense) of nonrenewable resource constraint; "<=" (default) or ">=" or "=".
            - weight (optional): Weight of resource. Non-negative integer or "inf" (default).

        - Return value: New resource object.

        - Example usage:

        >>> r = model.addResource("res1")

        >>> r = model.addResource("res1", {(0, 10): 1, (12, 100): 2})

        >>> r = model.addResource("res2", rhs=10, direction=">=")
        """
        if capacity is None:
            capacity = {}
        res = Resource(name=name, capacity=capacity, rhs=rhs, direction=direction, weight=weight)
        self.res.append(res)
        self.model_fields_set.add("res")
        # self.resources[res.name] = res
        return res

    def addTemporal(self, pred, succ, tempType="CS", delay=0, pred_mode=None, succ_mode=None):  # noqa: PLR0913 PLR0917
        """Add a temporal constraint to the model.

        A temporal constraint has the following form:

            predecessor's completion (start) time + delay <=
                            successor's start (completion) time.

        Parameter "delay" can be negative.

        - Arguments:
            - pred:
                Predecessor (an activity object) or string "source."
                Here, "source" specifies a dummy activity that precedes all other activities and starts at time 0.
            - succ:
                Successor (an activity object) or string "source."
                Here, "source" specifies a dummy activity that precedes all other activities and starts at time 0.
            - tempType (optional): String that differentiates the temporal type.
                "CS" (default)=Completion-Start, "SS"=Start-Start,
                "SC"= Start-Completion, "CC"=Completion-Completion.
            - delay (optional): Time lag between the completion (start) times of two activities.
            - pred_mode (optional): Predecessor's mode
            - succ_mode (optional): Successor's mode

        - Return value: New temporal object.

        - Example usage:

        >>> t=model.addTemporal(act1, act2)

        >>> t=model.addTemporal(act1, act2, tempType="SS", delay=-10)

        To specify the start time of activity act is exactly 50, we use two temporal constraints:

        >>> t=model.addTemporal("source", act, tempType="SS", delay=50)

        >>> t=model.addTemporal(act, "source", tempType="SS", delay=50)
        """
        # t = Temporal(pred, succ, tempType, delay)
        tempo = Temporal(pred=pred, succ=succ, type=tempType, delay=delay, pred_mode=pred_mode, succ_mode=succ_mode)
        self.tempo.append(tempo)
        self.model_fields_set.add("tempo")
        # self.temporals[pred.name, succ.name]=None
        return tempo

    def addState(self, name=""):
        """Add a state to the model.

        - Arguments:
            - name: Name for new state. Remark that strings in OptSeq are restricted to a-z, A-Z, 0-9, [], _ and @.

        - Return value: New state object.

        - Example usage:

        >>> a = model.addState("state1")
        """
        state = State(name=name)
        self.state.append(state)
        self.model_fields_set.add("states")
        # self.states[name]=s
        return state

    def update(self):  # noqa: C901 PLR0912
        """Prepare a string representing the current model in the OptSeq input format"""
        makespan = self.Params.Makespan

        f = []

        self.resources.clear()  # dictionary of resources that maps res-name to res-object
        if self.res:
            for r in self.res:
                self.resources[r.name] = r
                f.append(str(r))
            self.model_fields_set.add("resources")

        self.states.clear()  # dictionary of activities that maps state-name to state-object
        if self.state:
            for s in self.state:
                self.states[s.name] = s
                f.append(str(s))
            self.model_fields_set.add("states")

        self.modes.clear()  # dictionary of modes that maps mode-name to mode-object
        self.activities.clear()  # dictionary of activities that maps activity-name to activity-object
        if self.act:
            for a in self.act:
                #             if len(a.modes) >= 2:
                #                 for m in a.modes:
                #                     self.modes[m.name] = m

                # １つのモードと2つ以上を区別しない実装
                for m in a.modes:
                    self.modes[m.name] = m
            for k, v in self.modes.items():  # print mode information
                f.extend([f"mode {k} ", str(v)])

            for a in self.act:
                self.activities[a.name] = a
                f.append(str(a))
            self.model_fields_set.update({"modes", "activities"})

        # dictionary of temporal constraints that maps activity name pair to temporal-object
        self.temporals.clear()
        if self.tempo:
            for t in self.tempo:
                pred = t.pred if isinstance(t.pred, str) else t.pred.name
                succ = t.succ if isinstance(t.succ, str) else t.succ.name
                self.temporals[pred, succ] = t
                f.append(str(t))
            self.model_fields_set.add("temporals")

        # non-renewable constraint
        for r in self.res:
            self.resources[r.name] = r
            if len(r.terms) > 0:
                f.append(r.printConstraint())

        if makespan:
            f.append("activity sink duedate 0 \n")
        return " \n".join(f)

    def optimize(  # noqa: C901 PLR0912 PLR0914 PLR0915
        self,
        init_fn="optseq_best_act_data.txt",
        best_fn="optseq_best_act_data.txt",
        *,
        cloud=False,
    ):
        """Optimize the model using optseq.exe in the same directory.

        - Example usage:

        >>> model.optimize()
        """
        LOG = self.Params.OutputFlag
        f = self.update()
        if cloud:
            input_file_name = f"optseq_input{datetime.datetime.now().timestamp()}.txt"
            script = Path.cwd() / "scripts/optseq"
        else:
            input_file_name = "optseq_input.txt"
            script = str(Path(__file__).parent.resolve() / "optseq")
        with Path(input_file_name).open("w", encoding="utf-8") as f2:
            f2.write(f)

        if platform.system() == "Windows":
            cmd = "optseq "
        elif platform.system() == "Darwin":
            if platform.mac_ver()[2] == "arm64":  # model
                # cmd = f"{script}-m1 "  # Rosettaを使うことを想定
                cmd = f"{script}-mac "
            else:
                cmd = f"{script}-mac "
        elif platform.system() == "Linux":
            cmd = f"{script}-linux "
            # p = Path()  # 現在のフォルダ
            # github action でエラーするため消しておく
            # exe_file = p / "scripts/optseq-linux"
            # os.chmod(exe_file, 0o775)
        else:
            print(platform.system(), "may not be supported.")
        cmd += (
            "-time "
            + str(self.Params.TimeLimit)
            + " -backtrack  "
            + str(self.Params.Backtruck)
            + " -iteration  "
            + str(self.Params.MaxIteration)
            + " -report     "
            + str(self.Params.ReportInterval)
            + " -seed      "
            + str(self.Params.RandomSeed)
            + " -tenure    "
            + str(self.Params.Tenure)
            + " -neighborhood   "
            + str(self.Params.Neighborhood)
        )

        if self.Params.Initial:
            cmd += f" -initial {init_fn}"
        # print ("cmd=", cmd)
        try:
            if platform.system() == "Windows":
                # TODO: shell=Trueは不要なはず
                pipe = subprocess.Popen(  # noqa: S602
                    cmd.split(),
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )
            else:
                # TODO: shell=Trueは不要なはず
                pipe = subprocess.Popen(  # noqa: S602
                    cmd,
                    stdout=subprocess.PIPE,
                    stdin=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True,
                )
            if LOG:
                print("\n ================ Now solving the problem ================ \n")
            out, _err = pipe.communicate(f.encode())  # get the result

            if out == b"":
                print("error: could not execute command")
                print("please check that the solver is in the path")
                Path("optseq_error.txt").write_text("error: could not execute command", encoding="utf-8")
                self.Status = 7  # execution failed
                # exit(0)
                return

        except OSError:
            print("error: could not execute command")
            print("please check that the solver is in the path")
            Path("optseq_error.txt").write_text("error: could not execute command", encoding="utf-8")
            self.Status = 7  # execution failed
            # exit(0)
            return

        if cloud:
            Path(input_file_name).unlink()

        # for Python 3
        if int(sys.version_info[0]) >= 3:
            out = str(out, encoding="utf-8")

        if LOG == 2:
            print("\noutput:")
            print(out)
        if LOG:
            print("\nSolutions:")

        """
        optseq output file
        """
        if cloud:
            pass
        else:
            Path("optseq_output.txt").write_text(out, encoding="utf-8")

        # OptSeq didn't implement the return number
        # check the return code
        # self.Status = pipe.returncode
        # if self.Status !=0: #if the return code is not "optimal", then return
        #    print("Status=", self.Status)
        #    print("Output=", out)
        #    return

        # search strings
        infeasible = out.find("no feasible schedule found")
        if infeasible > 0:
            print("infeasible solution")
            self.Status = -1  # infeasible
            return
        self.Status = 0  # optimized
        s0 = "--- best solution ---"
        s1 = "--- tardy activity ---"
        s2 = "--- resource residuals ---"
        s3 = "--- best activity list ---"  # added for optseq 3.0
        s4 = "objective value ="
        pos0 = out.find(s0) + len(s0)  # job data start position
        pos1 = out.find(s1, pos0)  # data end position
        pos2 = out.find(s2, pos1)
        pos3 = out.find(s3, pos2)
        pos4 = out.find(s4, pos3)
        # print("data positions", pos0, pos1, pos2, pos3, pos4)
        data = out[pos0:pos1]
        res_data = out[pos2 + len(s2) : pos3]
        data = data.splitlines()
        res_lines = res_data.splitlines()
        # 目的関数値を得る
        remain_data = out[pos4:].split()
        self.ObjVal = int(remain_data[3])

        # save the best activity list
        best_act_data = out[pos3 + len(s3) : pos4]
        if cloud:
            pass
        else:
            Path(best_fn).write_text(best_act_data.lstrip(), encoding="utf-8")

        for line in res_lines:
            if len(line) <= 1:
                continue
            current = line.split()
            res_name = current[0][:-1]
            residual = current[1:]
            count = 0
            resDic = {}  # residual capacity
            while count < len(residual):
                interval = residual[count].split(",")
                int1 = int(interval[0][1:])
                int2 = int(interval[1][:-1])
                count += 1
                num = int(residual[count])
                count += 1
                resDic[int1, int2] = num
            # print(res_name, residual)
            self.resources[res_name].residual = resDic

        # job data conversion
        execute = []
        for i in range(len(data)):
            replaced = data[i].replace(",", " ")
            current = replaced.split()  # split by space
            # print(current)
            if len(current) > 1:
                execute.append(current)
        for line in execute:
            # print("line=", line)
            act_name = line[0]
            mode = line[1]
            try:
                start = line[2]
            except IndexError:
                print("Problem is infeasible")
                # exit(0)
                self.Status = -1
                return

            execute = line[3:-1]  # list for breakable activity
            completion = line[-1]
            if LOG:
                print(f"{act_name:>10} {mode:>5} {start:>5} {completion:>5}")
            # print("execute=", execute)
            if act_name in {"source", "sink"}:
                pass
            else:
                self.activities[act_name].start = int(start)
                self.activities[act_name].completion = int(completion)
                if mode != "---":
                    self.activities[act_name].selected = self.modes[mode]
                else:
                    self.activities[act_name].selected = self.activities[act_name].modes[0]
                exeDic = {}
                for exe in execute:
                    exe_data = exe.split("--")
                    start = exe_data[0]
                    completion = exe_data[1]
                    idx = completion.find("[")
                    # for parallel execution
                    if idx > 0:
                        parallel = completion[idx + 1 : -1]
                        completion = completion[:idx]
                        # print(completion, idx, parallel)
                    else:
                        parallel = 1
                    exeDic[int(start), int(completion)] = int(parallel)
                self.activities[act_name].execute = exeDic

    def write(self, filename="optseq_chart.txt"):  # noqa: C901 PLR0912 PLR0914 PLR0915
        """Output the gantt's chart as a text file.

        - Argument:
            - filename: Output file name. Default="optseq_chart.txt."

        - Example usage:

        >>> model.write("sample.txt")
        """
        f = Path(filename).open("w", encoding="utf-8")  # noqa: SIM115

        horizon = 0
        actList = []
        for a in self.activities:
            actList.append(a)
            act = self.activities[a]
            horizon = max(act.completion, horizon)
        # print("planning horizon=", horizon)
        actList.sort()
        title = " activity    mode".center(20) + " duration "

        width = len(str(horizon))  # period width = largest index of time
        for t in range(horizon):
            num = str(t + 1)
            title += num.rjust(width) + ""
        # print(title)
        f.write(title + "\n")
        f.write("-" * (30 + (width + 1) * horizon) + "\n")
        for a in actList:  # sorted order
            act = self.activities[a]  # act: activity object
            act_string = act.name.center(10)[:10]
            if len(act.modes) >= 2 and act.selected.name is not None:
                act_string += str(act.selected.name).center(10)
                act_string += str(self.modes[act.selected.name].duration).center(10)
                # print(" executed on resource:")
                # print(self.modes[act.selected.name].requirement, model.modes[act.selected.name].rtype)
            else:
                # print("executed on resource:")
                # print(act.modes[0].requirement, act.modes[0].rtype)
                act_string += str(act.modes[0].name).center(10)[:10]
                act_string += str(act.modes[0].duration).center(10)
            execute = [0 for t in range(horizon)]
            for s, c in act.execute:
                para = act.execute[s, c]
                for t in range(s, c):
                    execute[t] = int(para)

            for t in range(horizon):
                if execute[t] >= 2:
                    # for res_name in self.modes[act.selected.name].requirement:
                    # print(res_name)
                    # print(model.modes[act.selected.name].rtype)
                    # print(self.modes[act.selected.name])
                    act_string += "*" + str(execute[t]).rjust(width - 1)
                elif execute[t] == 1:
                    act_string += "" + "=" * (width)
                elif t >= act.start and t < act.completion:
                    act_string += "" + "." * (width)
                else:
                    act_string += "" + " " * width
            act_string += ""
            # print(act_string)
            f.write(act_string + "\n")
        # print(act.name + "  starts at " + str(act.start) + " and finish at " + str(act.completion))
        # print("  and is executed :" + str(act.execute)])

        f.write("-" * (30 + (width + 1) * horizon) + "\n")
        f.write("resource usage/capacity".center(30) + " \n")
        f.write("-" * (30 + (width + 1) * horizon) + "\n")
        resList = list(self.resources)
        resList.sort()
        for r in resList:
            res = self.resources[r]
            if len(res.terms) == 0:  # output residual and capacity
                r_string = res.name.center(30)
                cap = [0 for t in range(horizon)]
                residual = [0 for t in range(horizon)]
                for sc in res.residual:
                    s, c = sc
                    amount = res.residual[s, c]
                    if c == "inf":
                        c = horizon
                    s = min(s, horizon)
                    c = min(c, horizon)
                    for t in range(s, c):
                        residual[t] += amount

                for sc in res.capacity:
                    s, c = sc
                    amount = res.capacity[s, c]
                    if c == "inf":
                        c = horizon
                    s = min(s, horizon)
                    c = min(c, horizon)
                    for t in range(s, c):
                        cap[t] += amount

                for t in range(horizon):
                    num = str(cap[t] - residual[t])
                    r_string += "" + num.rjust(width)
                f.write(r_string + "\n")

                r_string = " ".center(30)

                for t in range(horizon):
                    num = str(cap[t])
                    r_string += "" + num.rjust(width)
                f.write(r_string + "\n")
                f.write("-" * (30 + (width + 1) * horizon) + "\n")
        f.close()

    def writeExcel(self, filename="optseq_chart.csv", scale=1):  # noqa: C901 PLR0912 PLR0914 PLR0915
        """Output the gantt's chart as a csv file for printing using Excel.

        - Argument:
            - filename: Output file name. Default="optseq_chart.csv."

        - Example usage:

        >>> model.writeExcel("sample.csv")
        """
        f = Path(filename).open("w", encoding="utf-8")  # noqa: SIM115
        horizon = 0
        actList = []
        for a in self.activities:
            actList.append(a)
            act = self.activities[a]
            horizon = max(act.completion, horizon)
        # print("planning horizon=", horizon)
        if scale <= 0:
            print("optseq write scale error")
            sys.exit()
        original_horizon = horizon
        horizon = int(horizon / scale) + 1
        actList.sort()
        title = " activity ,   mode,".center(20) + " duration,"
        width = len(str(horizon))  # period width = largest index of time
        for t in range(horizon):
            num = str(t + 1)
            title += num.rjust(width) + ","
        f.write(title + "\n")
        for a in actList:  # sorted order
            act = self.activities[a]  # act: activity object
            act_string = act.name.center(10)[:10] + ","
            if len(act.modes) >= 2:
                act_string += str(act.selected.name).center(10) + ","
                act_string += str(self.modes[act.selected.name].duration).center(10) + ","
            else:
                act_string += str(act.modes[0].name).center(10)[:10] + ","
                act_string += str(act.modes[0].duration).center(10) + ","
            execute = [0 for t in range(horizon)]
            for s, c in act.execute:
                para = act.execute[s, c]
                for t in range(s, c):
                    t2 = int(t / scale)
                    execute[t2] = int(para)
            for t in range(horizon):
                if execute[t] >= 2:
                    act_string += "*" + str(execute[t]).rjust(width - 1) + ","
                elif execute[t] == 1:
                    act_string += "" + "=" * (width) + ","
                elif t >= int(act.start / scale) and t < int(act.completion / scale):
                    act_string += "" + "." * (width) + ","
                else:
                    act_string += "" + " " * width + ","
            f.write(act_string + "\n")
        resList = list(self.resources)
        resList.sort()

        for r in resList:
            res = self.resources[r]
            if len(res.terms) == 0:  # output residual and capacity
                r_string = res.name.center(30) + ", , ,"
                cap = [0 for t in range(horizon)]
                residual = [0 for t in range(horizon)]
                for sc in res.residual:
                    s, c = sc
                    amount = res.residual[s, c]
                    if c == "inf":
                        c = horizon
                    s = min(s, original_horizon)
                    c = min(c, original_horizon)
                    s2 = int(s / scale)
                    c2 = int(c / scale)
                    for t in range(s2, c2):
                        residual[t] += amount

                for sc in res.capacity:
                    s, c = sc
                    amount = res.capacity[s, c]
                    if c == "inf":
                        c = horizon
                    s = min(s, original_horizon)
                    c = min(c, original_horizon)
                    s2 = int(s / scale)
                    c2 = int(c / scale)
                    for t in range(s2, c2):
                        cap[t] += amount

                for t in range(horizon):
                    # num = str(cap[t] - residual[t])
                    r_string += str(residual[t]) + ","
                f.write(r_string + "\n")

                # r_string = str(" ").center(30) + ", , ,"
                #
                # for t in range(horizon):
                #    num = str(cap[t])
                #    r_string += "" + num.rjust(width) + ","
                # f.write(r_string + "\n")
        f.close()


def make_gantt(model, start="2019/1/1", period="days"):
    """ガントチャートを生成する関数"""
    import pandas as pd  # noqa: PLC0415
    import plotly.figure_factory as ff  # noqa: PLC0415

    start = pd.to_datetime(start)

    def time_convert_long(periods):
        if period == "days":
            time_ = start + datetime.timedelta(days=float(periods))
        elif period == "hours":
            time_ = start + datetime.timedelta(hours=float(periods))
        elif period == "minutes":
            time_ = start + datetime.timedelta(minutes=float(periods))
        elif period == "seconds":
            time_ = start + datetime.timedelta(seconds=float(periods))
        else:
            msg = "period must be 'days' or 'seconds' or minutes' or 'days'"
            raise ValueError(msg)
        return time_.strftime("%y-%m-%d %H:%M:%S")

    L = []
    for i in model.activities:
        a = model.activities[i]
        # res = None
        for _r in a.modes[0].requirement:  # key
            # res = _r[0]
            break
        # print(a.name, a.start, a.completion,res)
        st = time_convert_long(a.start)
        fi = time_convert_long(a.completion)

        L.append({"Task": a.name, "Start": st, "Finish": fi})

    # 可視化するデータと色の情報をplotly.figure_factory.create_gantt()に渡す
    return ff.create_gantt(
        L,
        index_col=None,
        title="Task View",
        show_colorbar=False,
        showgrid_x=True,
        showgrid_y=True,
        group_tasks=False,
    )


def make_resource_graph(model):  # noqa: C901 PLR0912
    """資源の使用量と残差(容量-使用量)を図示する関数"""
    import plotly.graph_objs as go  # noqa: PLC0415
    from plotly.subplots import make_subplots  # noqa: PLC0415

    horizon = 0
    for a in model.act:
        horizon = max(a.completion, horizon)
    # print("planning horizon=",horizon)

    count = 0
    for res in model.res:
        if len(res.terms) == 0:  # renewable resource
            count += 1
            # print(count)
            cap = [0 for t in range(horizon)]
            residual = [0 for t in range(horizon)]
            usage = [0 for t in range(horizon)]
            for sc in res.residual:
                s, c = sc
                amount = res.residual[s, c]
                if c == "inf":
                    c = horizon
                s = min(s, horizon)
                c = min(c, horizon)
                for t in range(s, c):
                    residual[t] += amount

            for sc in res.capacity:
                s, c = sc
                amount = res.capacity[s, c]
                if c == "inf":
                    c = horizon
                s = min(s, horizon)
                c = min(c, horizon)
                for t in range(s, c):
                    cap[t] += amount

            for t in range(horizon):
                usage[t] = cap[t] - residual[t]
    if count >= 1:
        fig = make_subplots(rows=len(model.res), cols=1, subplot_titles=[r.name for r in model.res])

        x = list(range(horizon))
        for i, _res in enumerate(model.res):
            fig.add_trace(
                go.Bar(name="Usage", x=x, y=usage, marker_color="crimson"),
                row=i + 1,
                col=1,
            )
            fig.add_trace(
                go.Bar(name="Residual", x=x, y=residual, marker_color="lightslategrey"),
                row=i + 1,
                col=1,
            )
        fig.update_layout(barmode="stack", title_text="Capacity/Usage", showlegend=False)
    else:
        fig = {}
    return fig
